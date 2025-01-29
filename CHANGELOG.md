# Changelog

All notable changes to this project will be documented in this file.

## [0.5.0] - 2024-09-21

### Added

- Batched scraper over all courts
- More logging around captcha solver
- Added SQL indexes for improved query performance

### Changed

- Cursor based pagination for efficient queries

### Fixed

- Updated scraper logic for Moscow courts
- Many different scraper bugs
- Removed invalid HTTP headers on scraper requests

## [0.4.2] - 2024-06-11

### Added

- More courts and articles to scrape
    ```
    1zovs--spb
    2vovs--cht
    gor-kluch--krd
    groznensky--chn
    oblsud--kln
    oblsud--lo
    oblsud--vol
    sankt-peterburgsky--spb
    ```

    ```
    213
    214
    244
    329
    ```

## [0.4.1] - 2024-06-11

### Added

- "clean-sessions" task to remove outdated and unimportant scrape sessions
- Indicate captcha status in debug message of scrape session

### Changed

- Improve detection of updated cases through applying string sanitization to fields
- Create temporary file in OS for downloaded captcha images

### Fixed

- Broken docker image by using Debian as Alpine Linux was not compatible with Torch anymore

## [0.4.0] - 2024-06-09

### Added

- Detect and solve captchas with ML (Convolution) model
- Utility script to convert Amnezia VPN config for Docker setup

## [0.3.1] - 2023-09-12

### Changed

- More articles for scraper: 328, 332, 337, 338, 339

### Fixed

- Updated cases were shown in history, even though nothing changed
- Handle race conditions which violate UNIQUE constraint of cases in database

## [0.3.0] - 2023-09-03

### Added

- Filter by judge, dates, courts and regions
- Show scrape sessions and results
- Show history of changes for each case
- New navigation
- Scrape moscow courts
- Show result and effective date in cases results
- OpenVPN + Cloak client docker container for VPN networking

### Changed

- Improved filter interface
- Refactored React pagination logic

## [0.2.1] - 2023-07-23

### Added

- Search for multiple articles and "defendants" by separating them with a comma

## [0.2.0] - 2023-07-21

### Added

- Pagination for Query API
- Current search and selected page shows now in the URL as parameters which makes it easier to share search results with others

### Changed

- Frontend UI from endless scrolling to pagination. This helps a) to have less data to load per search b) fixes the issue where text was hard to copy & paste

### Fixed

- Celery schedule addressed the "scrape all" task wrongly

## [0.1.0] - 2023-05-04

- Initial release
