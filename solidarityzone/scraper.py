import datetime
import math
import random
import re
import tempfile
import time
import urllib
from enum import Enum

import requests
from bs4 import BeautifulSoup
from celery.utils.log import get_task_logger

from .captcha import solve_captcha
from .utils import insert_into_dict

MAX_CAPTCHA_SOLVE_ATTEMPTS = 5

MIN_DELAY_SEC = 2
MAX_DELAY_SEC = 20


class ErrorType(Enum):
    # Server is currently not reachable because of an internal server error or
    # too much traffic, usually a request during a different time will fix that
    SERVER_UNAVAILABLE = "server_unavailable"

    # We've got blocked .. needs a VPN or a better one :-D
    ACCESS_BLOCKED = "access_blocked"

    # The parser did not know what to do with this, maybe an implementation bug
    # or the HTML page changed and it needs adjustment
    UNKNOWN_PAGE = "unknown_page"

    # The parser tried to detect captcha for 5 times, never succeeded
    CAPTCHA_FAILED = "captcha_failed"

    # Something bad happenend!
    UNKNOWN_ERROR = "unknown_error"

    def __str__(self) -> str:
        return self.value


class CourtScraper:
    def __init__(self, court_code, log=True):
        self.logger = None
        if log is True:
            self.logger = get_task_logger(__name__)
        self.court_code = court_code
        self.translate_dict = {
            "Номер дела ~ материала": "case_number",
            "№ дела": "case_number",
            "Номер дела": "case_number",
            "Карточка дела": "url",
            "Статьи": "articles",
            "Дата поступления": "entry_date",
            "Дата поступления дела": "entry_date",
            "Дата поступления дела в апелляционную инстанцию": "entry_date",
            "Дата рассмотрения дела в первой инстанции": "result_date",
            "Дата решения": "result_date",
            "Дата окончания": "result_date",
            "Дата вступления решения в силу": "effective_date",
            "Дата вступления в законную силу": "effective_date",
            "Судья": "judge_name",
            "Суд первой инстанции, судья": "judge_name",
            "Решение": "result",
            "Результат рассмотрения": "result",
            "Результат": "result",
            "Судебные акты": "documents",
            "Лица": "defendant_name",
        }
        self.case_subtypes = {
            "Первая инстанция": "u1_case",
            "Апелляционная инстанция": "u2_case",
        }
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        }

    def translate_table_ru_en(self, table):
        new_table = {
            "articles": None,
            "case_number": None,
            "defendant_name": None,
            "effective_date": None,
            "entry_date": None,
            "judge_name": None,
            "result": None,
            "result_date": None,
            "sub_type": None,
            "url": None,
        }
        for k, v in table.items():
            if k in self.translate_dict:
                new_table[self.translate_dict[k]] = v
                if "date" in self.translate_dict[k]:
                    try:
                        new_table[self.translate_dict[k]] = datetime.datetime.strptime(
                            v, "%d.%m.%Y"
                        ).date()
                    except ValueError:
                        # This might fail as sometimes the courts write a
                        # text here (something like "pending" etc.) instead
                        # of a date
                        new_table[self.translate_dict[k]] = None
            if v == "":
                new_table[self.translate_dict[k]] = None
        return new_table

    def log(self, message, log_type="info"):
        if self.logger is not None:
            if log_type == "info":
                self.logger.info(message)
            elif log_type == "warn":
                self.logger.warn(message)

    def parse_search_exception(
        self, text, url, request_res, status_code, captcha_attempts=0
    ):
        if "Данных по запросу не обнаружено" in text:
            self.log("No results")
            request_res["result"] = []

        elif "временно недоступен" in text or "Информация временно недоступна" in text:
            self.log("Server unavailable")
            request_res["error"] = True
            request_res["error_type"] = ErrorType.SERVER_UNAVAILABLE
            request_res["error_debug_message"] = "Server is unavailable ({})".format(
                status_code
            )
            request_res["url"].append(url)

        elif "запрос заблокирован по соображениям безопасности" in text:
            self.log("Server blocked")
            request_res["error"] = True
            request_res["error_type"] = ErrorType.ACCESS_BLOCKED
            request_res[
                "error_debug_message"
            ] = "Access to server is blocked ({})".format(status_code)
            request_res["url"].append(url)

        elif "Неверно указан проверочный код с картинки" in text:
            self.log("Captcha not detected")
            request_res["error"] = True
            request_res["is_captcha_successful"] = False
            request_res["error_type"] = ErrorType.CAPTCHA_FAILED
            request_res[
                "error_debug_message"
            ] = "Captcha not solved in {} attempts".format(captcha_attempts)
            request_res["url"].append(url)

        else:
            self.log("An unknown page was encountered")
            request_res["error"] = True
            request_res["error_type"] = ErrorType.UNKNOWN_PAGE
            request_res[
                "error_debug_message"
            ] = "An unknown page was encountered ({}): {}".format(status_code, text)
            request_res["url"].append(url)
        return request_res

    def parse_page(self):
        pass

    def get_court_data(self, articles, case_subtype, entry_date, result_date):
        pass


class CourtScraperRegion(CourtScraper):
    def __init__(self, court_code):
        super().__init__(court_code)
        self.court_code = court_code
        self.court_url = f"https://{court_code}.sudrf.ru"

    def parse_page(self, page, case_subtype, s):
        soup = BeautifulSoup(page, "html.parser")
        all_res = []

        tablecont = soup.find("table", {"id": "tablcont"})
        if tablecont is None:
            self.log("Could not find #tablecont table in results page", "warn")
            return all_res
        # parse table by rows. one row = one case
        for i, tr in enumerate(tablecont.find_all("tr")):
            # read table header
            if i == 0:
                fields = tr.find_all("th")
                for i in range(len(fields)):
                    fields[i] = fields[i].get_text(separator=" ").strip()
            else:
                columns = tr.find_all("td")

                res = {"Карточка дела": None}
                for field, col in zip(fields, columns):
                    field = (
                        field.replace("c", "с")
                        .replace("o", "о")
                        .replace("e", "е")
                        .replace("a", "а")
                        .replace("p", "р")
                    )
                    if field != "Судебные акты":
                        col_val = col.get_text(strip=True, separator="\n").splitlines()

                        if field == "№ дела":
                            res["Карточка дела"] = self.court_url + col.a.get("href")

                    else:
                        col_val = []
                        for doc in col.find_all("a"):
                            col_val.append(self.court_url + doc.get("href"))
                    res[field] = col_val

                # parse persons from the case card
                r = s.get(url=res["Карточка дела"])
                time.sleep(random.randint(MIN_DELAY_SEC, MAX_DELAY_SEC))
                text = r.text
                soup = BeautifulSoup(text, "html.parser")

                case_card = soup.find("ul", {"class": "tabs"})
                if case_card is None:
                    self.log("Could not parse case card", "warn")

                else:
                    # find a table with persons
                    persons = soup.find("div", {"class": "contentt"}).find_all("div")
                    persons_id = [
                        i for i, p in enumerate(persons) if "Перечень статей" in str(p)
                    ]
                    # parse table by rows. one row = one person
                    for i_person, tr_person in enumerate(
                        persons[persons_id[0]].find_all("tr")[2:]
                    ):
                        cols = tr_person.find_all("td")
                        res_1 = res.copy()
                        res_1["Лица"] = cols[0].get_text(strip=True)
                        res_1["Статьи"] = cols[1].get_text(strip=True)

                        # get rid of lists in the result dictionary
                        for k, v in res_1.items():
                            if isinstance(v, list) and k != "Судебные акты":
                                res_1[k] = " ".join(v)
                            else:
                                res_1[k] = v
                        res_1 = self.translate_table_ru_en(res_1)
                        res_1["sub_type"] = case_subtype
                        res_1["court_code"] = self.court_code
                        all_res.append(res_1)
        return all_res

    def get_court_data(
        self,
        article,
        case_subtype="Первая инстанция",
        entry_date={"from": "24.02.2022", "to": ""},
        result_date={"from": "", "to": ""},
    ):
        u_case = self.case_subtypes[case_subtype]
        article_str = ""

        if isinstance(article, str):
            article_str = article

        court_request_url = self.court_url + "/modules.php?"
        if u_case == "u1_case":
            request_params = {
                "name": "sud_delo",
                "srv_num": 1,
                "name_op": "r",
                "delo_id": 1540006,
                "case_type": 0,
                "new": 0,
                "U1_DEFENDANT__NAMESS": "",
                "u1_case__CASE_NUMBERSS": "",
                "u1_case__JUDICIAL_UIDSS": "",
                "delo_table": "u1_case",
                "u1_case__ENTRY_DATE1D": entry_date["from"],
                "u1_case__ENTRY_DATE2D": entry_date["to"],
                "U1_CASE__JUDGE": "",
                "u1_case__RESULT_DATE1D": result_date["from"],
                "u1_case__RESULT_DATE2D": result_date["to"],
                "U1_CASE__RESULT": "",
                "U1_CASE__BUILDING_ID": "",
                "U1_CASE__COURT_STRUCT": "",
                "U1_EVENT__EVENT_NAME": "",
                "U1_EVENT__EVENT_DATEDD": "",
                "U1_DEFENDANT__LAW_ARTICLESS": article_str,
                "U1_DEFENDANT__RESULT_DATE1D": "",
                "U1_DEFENDANT__RESULT_DATE2D": "",
                "U1_DEFENDANT__RESULT": "",
                "U1_PARTS__PARTS_TYPE": "",
                "U1_PARTS__INN_STRSS": "",
                "U1_PARTS__KPP_STRSS": "",
                "U1_PARTS__OGRN_STRSS": "",
                "U1_PARTS__OGRNIP_STRSS": "",
                "U1_DOCUMENT__PUBL_DATE1D": "",
                "U1_DOCUMENT__PUBL_DATE2D": "",
                "U1_CASE__VALIDITY_DATE1D": "",
                "U1_CASE__VALIDITY_DATE2D": "",
                "U1_ORDER_INFO__ORDER_DATE1D": "",
                "U1_ORDER_INFO__ORDER_DATE2D": "",
                "U1_ORDER_INFO__ORDER_NUMSS": "",
                "U1_ORDER_INFO__EXTERNALKEYSS": "",
                "U1_ORDER_INFO__STATE_ID": "",
                "U1_ORDER_INFO__RECIP_ID": "",
                "Submit": "Найти",
            }

        elif u_case == "u2_case":
            request_params = {
                "name": "sud_delo",
                "srv_num": 1,
                "name_op": "r",
                "delo_id": 4,
                "case_type": 0,
                "new": 4,
                "U2_DEFENDANT__NAMESS": "",
                "u2_case__CASE_NUMBERSS": "",
                "u2_case__JUDICIAL_UIDSS": "",
                "delo_table": "u2_case",
                "u2_case__ENTRY_DATE1D": entry_date["from"],
                "u2_case__ENTRY_DATE2D": entry_date["to"],
                "U2_CASE__COURT_I_REGION_ID": "",
                "U2_CASE__COURT_I": "",
                "U2_CASE__CASE_NUMBER_ISS": "",
                "U2_CASE__JUDGE": "",
                "u2_case__RESULT_DATE1D": result_date["from"],
                "u2_case__RESULT_DATE2D": result_date["to"],
                "U2_CASE__RESULT": "",
                "U2_CASE__BUILDING_ID": "",
                "U2_CASE__JUDGE_I": "",
                "U2_CASE__COURT_STRUCT": "",
                "U2_EVENT__EVENT_DATEDD": "",
                "U2_DEFENDANT__LAW_ARTICLESS": article_str,
                "U2_DEFENDANT__M_SUB_TYPE": "",
                "U2_DEFENDANT__RESULT": "",
                "U2_PARTS__PARTS_TYPE": "",
                "U2_PARTS__INN_STRSS": "",
                "U2_PARTS__KPP_STRSS": "",
                "U2_PARTS__OGRN_STRSS": "",
                "U2_PARTS__OGRNIP_STRSS": "",
                "U2_DOCUMENT__PUBL_DATE1D": "",
                "U2_DOCUMENT__PUBL_DATE2D": "",
                "U2_DOCUMENT__VALIDITY_DATE1D": "",
                "U2_DOCUMENT__VALIDITY_DATE2D": "",
                "Submit": "Найти",
            }

        if isinstance(article, list):
            request_params["lawbookarticles[]"] = article

        url = court_request_url + urllib.parse.urlencode(
            request_params, encoding="1251", doseq=True
        )
        request_res = {
            "error": False,
            "error_type": None,
            "error_debug_message": None,
            "url": [url],
            "is_captcha": False,
            "is_captcha_successful": False,
            "result": [],
        }

        try:
            self.log("Make initial request ..")
            s = requests.Session()
            s.headers = self.headers
            r = s.get(url=url)
            text = r.text
            captcha_attempts = 0
            request_params_cap = None
            while (
                "Неверно указан проверочный код с картинки" in text
            ) and captcha_attempts < MAX_CAPTCHA_SOLVE_ATTEMPTS:
                request_res["is_captcha"] = True

                url = (
                    court_request_url
                    + "name=sud_delo&srv_num=1&name_op=sf&delo_id=1540005"
                )
                time.sleep(random.randint(MIN_DELAY_SEC, MAX_DELAY_SEC))
                r = s.get(url=url)

                # retrieve captcha image and id
                captcha_page_parsed = BeautifulSoup(r.text, "html.parser")
                captcha_id_el = captcha_page_parsed.find("input", {"name": "captchaid"})
                captcha_attempts += 1
                try:
                    captcha_id = captcha_id_el["value"]
                    captcha_img_url = captcha_id_el.parent.find("img")["src"]
                    captcha_img_url = captcha_img_url.replace(" ", "")

                    # download and solve captcha
                    file = tempfile.NamedTemporaryFile(suffix=f"-{self.court_code}.png")
                    captcha_path = file.name
                    urllib.request.urlretrieve(captcha_img_url, captcha_path)
                    captcha = solve_captcha(captcha_path)
                    file.close()

                    request_params_cap = insert_into_dict(
                        request_params, 12, "captcha", captcha
                    )
                    request_params_cap = insert_into_dict(
                        request_params_cap, 13, "captchaid", captcha_id
                    )

                    url = court_request_url + urllib.parse.urlencode(
                        request_params_cap, encoding="1251", doseq=True
                    )
                    r = s.get(url=url)
                    text = r.text
                    self.log(f"Detected captcha {captcha}")
                    request_res["url"].append(url)

                except Exception as e:
                    self.log(
                        f" Could not locate and/or retrieve a captcha image from the page. Error text: {e}",
                        "warn",
                    )
                    text = ""

            if request_params_cap:
                request_params = request_params_cap.copy()

            re_n_results = (
                "Всего по запросу найдено — \d+\. На странице записи с 1\s*по \d+\."
            )

            if re.search(re_n_results, text):
                request_res["is_captcha_successful"] = True
                n_results_text = re.search(re_n_results, text).group(0)
                n_results, first_page, last_page = re.findall("\d+", n_results_text)
                n_pages = math.ceil(int(n_results) / int(last_page))

                if n_pages > 1:
                    self.log("Detected {} pages".format(n_pages + 1))
                    vnkod = re.search("vnkod=\w+&", text).group(0)[6:-1]

                    for i in range(1, n_pages + 1):
                        self.log("Request page {} ..".format(i))
                        request_params["vnkod"] = vnkod
                        request_params["page"] = i
                        url = court_request_url + urllib.parse.urlencode(
                            request_params, encoding="1251"
                        )

                        # No need to make a request for the first page as we already did that
                        if i > 1:
                            time.sleep(random.randint(MIN_DELAY_SEC, MAX_DELAY_SEC))
                            r = s.get(url=url)
                        results = self.parse_page(r.text, case_subtype, s)
                        self.log("Added {} results".format(len(results)))
                        request_res["result"].extend(results)
                        request_res["url"].append(url)

                else:
                    request_res["result"] = self.parse_page(text, case_subtype, s)
                    self.log("Added {} results".format(len(request_res["result"])))
                    request_res["url"].append(url)

            else:
                request_res = self.parse_search_exception(
                    text, url, request_res, r.status_code, captcha_attempts
                )

            s.close()

        except Exception as e:
            self.log("An unknown error occurred")
            self.logger.exception(
                "court_code={}, article={}, url={}".format(
                    self.court_code, article, url
                )
            )
            request_res["error"] = True
            request_res["error_type"] = ErrorType.UNKNOWN_ERROR
            request_res["error_debug_message"] = str(e)
            request_res["url"].append(url)

        request_res["url"] = list(set(request_res["url"]))
        return request_res


class CourtScraperMoscow(CourtScraper):
    # Use the meta search page "mos-gorsud.ru" for scraping cases in Moscow region
    HOST = "www.mos-gorsud.ru"

    def __init__(self):
        super().__init__("mos-gorsud")
        self.court_url = f"https://{self.HOST}"

        self.case_subtypes = {
            "Первая инстанция": 1,
            "Апелляционная инстанция": 2,
        }

    def parse_page(self, page, case_subtype, s):
        all_res = []
        all_urls = []

        links = []
        soup = BeautifulSoup(page, "html.parser")
        for row in soup.find_all("nobr"):  # ("a", "detailsLink")
            row_link = row.find("a", "detailsLink")
            if row_link:
                links.append(self.court_url + row_link.get("href"))

        for link in links:
            s = requests.Session()
            s.headers = self.headers
            time.sleep(random.randint(MIN_DELAY_SEC, MAX_DELAY_SEC))
            r = s.get(url=link)
            all_urls.append(link)

            soup = BeautifulSoup(r.text, "html.parser")
            result = soup.find_all("div", "main searchDetails")
            res_1 = {}
            if len(result) == 0:
                self.log("Could not parse a Moscow court case card", "warn")

            else:
                persons_div = None
                result_rows = result[0].find_all("div", "row_card")
                for result_row in result_rows:
                    k = result_row.find("div", "left").get_text().strip()
                    k = (
                        k.replace("c", "с")
                        .replace("o", "о")
                        .replace("e", "е")
                        .replace("a", "а")
                        .replace("p", "р")
                    )
                    if "подсудимый" in k.lower() or "осужденный" in k.lower():
                        persons_div = result_row.find("div", "right")
                    else:
                        v = result_row.find("div", "right").get_text().strip()
                        res_1[k] = v

                res_1 = self.translate_table_ru_en(res_1)
                res_1["sub_type"] = case_subtype
                res_1["documents"] = link + "#tabs-3"
                res_1["url"] = link

                # We're scraping a meta search page for many courts, identify which court we're currently looking at
                court_code = re.findall(self.court_url + "/(.+)/services", link)[0]
                if court_code[:3] == "rs/":
                    court_code = court_code[3:] + ".msk"
                res_1["court_code"] = court_code

                if persons_div is None:
                    self.log(
                        "Could not find a column with the defendant name(s)", "warn"
                    )
                else:
                    persons = persons_div.find_all("span")
                    articles = re.findall("\((.+)\)", persons_div.get_text())
                    for i in range(len(persons)):
                        res_1["defendant_name"] = persons[i].get_text()
                        res_1["articles"] = articles[i]
                        all_res.append(res_1.copy())

        return all_res, all_urls

    def get_court_data(
        self,
        article,
        case_subtype="Первая инстанция",
        entry_date={"from": "24.02.2022", "to": ""},
        result_date={"from": "", "to": ""},
    ):
        u_case = self.case_subtypes[case_subtype]
        court_request_url = self.court_url + "/search?"
        url = (
            court_request_url
            + f"caseDateFrom={entry_date['from']}&codex={article}&instance={u_case}&processType=6&formType=fullForm&page=1"
        )

        request_res = {
            "error": False,
            "error_type": None,
            "error_debug_message": None,
            "url": [url],
            "is_captcha": False,
            "is_captcha_successful": True,
            "result": [],
        }

        try:
            self.log("Make initial request ..")
            s = requests.Session()
            s.headers = self.headers
            r = s.get(url=url)
            # r.encoding = "utf-8"  # override encoding manually
            text = r.text

            if "По вашему запросу найдено записей" in r.text:
                soup = BeautifulSoup(text, "html.parser")
                max_page = soup.find("input", {"id": "paginationFormMaxPages"})

                if max_page:
                    n_pages = int(max_page.get("value"))
                    self.log("Detected {} pages".format(n_pages + 1))

                    for i in range(1, n_pages + 1):
                        self.log("Request page {} ..".format(i))
                        if i > 1:
                            url = (
                                court_request_url
                                + f"caseDateFrom={entry_date['from']}&caseDateTo={entry_date['to']}&codex={article}&processType=6&formType=fullForm&page={i}"
                            )
                            r = s.get(url=url)
                            # r.encoding = "utf-8"  # override encoding manually

                        results, urls = self.parse_page(r.text, case_subtype, s)
                        self.log("Added {} results".format(len(results)))

                        request_res["result"].extend(results)
                        request_res["url"].extend([url] + urls)

                else:
                    results, urls = self.parse_page(text, case_subtype, s)
                    self.log("Added {} results".format(len(request_res["result"])))
                    request_res["result"] = results
                    request_res["url"].extend([url] + urls)

            else:
                request_res = self.parse_search_exception(
                    text, url, request_res, r.status_code
                )

            s.close()

        except Exception as e:
            self.log("An unknown error occurred")
            self.logger.exception(
                "court_code={}, article={}, url={}".format(
                    self.court_code, article, url
                )
            )
            request_res["error"] = True
            request_res["error_type"] = ErrorType.UNKNOWN_ERROR
            request_res["error_debug_message"] = str(e)
            request_res["url"].append(url)

        request_res["url"] = list(set(request_res["url"]))

        return request_res
