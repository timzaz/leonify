import logging
import time
import typing
from functools import lru_cache

from fastapi import HTTPException
from fastapi.applications import FastAPI
from fastapi.param_functions import Query
from fastapi.requests import Request
from pydantic import BaseModel
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

eur_id: str = "wb_Text51"
gbp_id: str = "wb_Text8"
usd_id: str = "wb_Text78"
_driver: WebDriver | None = None
_start = time.time()


class Error(BaseModel):
    error: str


class Leones(BaseModel):
    leones: float
    time: float


def get_driver() -> WebDriver:
    global _driver

    if _driver is not None:
        return _driver

    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--ignore-certificate-errors")

    _driver = webdriver.Chrome(options=options)
    _driver.get("https://bsl.gov.sl")
    _driver.implicitly_wait(10)

    return _driver


@lru_cache
def get_value(driver: WebDriver, id: str) -> str:
    try:
        wait = WebDriverWait(driver, 3)
        element: WebElement = wait.until(
            EC.presence_of_element_located((By.ID, id))
        )
        return (
            "".join(
                [
                    x
                    for x in element.find_element(
                        By.TAG_NAME, "strong"
                    ).text.split("SLE")[1:]
                ]
            )
            .strip()
            .replace(",", "")
        )
    except TimeoutException as exc:
        logger.error(f"BSL server could be temporarily down: {exc}")
        raise HTTPException(500, "BSL server temporarily down.")


application = FastAPI(
    title="Leonify",
    description=(
        "BSL Forex Converter - returns the leones value for given currency."
    ),
)


@application.on_event("startup")
async def on_startup():
    global _start
    get_driver()
    processing: str = f"Started in: {time.time() - _start}"
    logger.info(processing)


@application.on_event("shutdown")
async def on_shutdown():
    driver: WebDriver = get_driver()
    driver.quit()


@application.exception_handler(400)
@application.exception_handler(500)
async def exception_handler(
    _: Request,
    exc: typing.Union[
        Exception,  #: Just to be safe
        HTTPException,  #: Just to be safe
    ],
) -> JSONResponse:
    """Global exception handler"""

    e = exc
    return JSONResponse(
        {"error": (getattr(e, "detail") if hasattr(e, "detail") else f"{e}")}
    )


@application.get(
    "/",
    response_model=Leones,
    responses={200: {"model": Leones}, 400: {"model": Error}},
    status_code=200,
)
async def index(
    request: Request,
    eur: float
    | None = Query(
        None,
        title="The Euro value to convert",
    ),
    gbp: float
    | None = Query(
        None,
        title="The Great Britain Pound value to convert",
    ),
    usd: float
    | None = Query(
        None,
        title="The United States Dollar value to convert",
    ),
):
    """Index route."""

    start = time.time()
    #: User must supply 1 and only 1 query parameter value
    if (eur is None and gbp is None and usd is None) or (
        len(
            [
                x
                for x in (
                    eur,
                    gbp,
                    usd,
                )
                if x is not None
            ]
        )
        != 1
    ):
        raise HTTPException(400, "Ambiguous request.")

    leones: float | None = None
    driver: WebDriver = get_driver()
    if eur is not None:
        leones = eur * float(get_value(driver, eur_id).replace(",", ""))
    elif gbp is not None:
        leones = gbp * float(get_value(driver, gbp_id).replace(",", ""))
    else:
        usd = typing.cast(float, usd)
        leones = usd * float(get_value(driver, usd_id).replace(",", ""))

    duration = time.time() - start
    return Leones(leones=leones, time=duration)
