import logging
import uvicorn
import threading
from fastapi import FastAPI, Body, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from pipeline.pipeline import Pipeline

logger = logging.getLogger(__name__)


class PipelineConfigurator:
    """
    API to set pipeline settings.
    """
    def __init__(self, pipeline: Pipeline, all_settings, host: str, port: int):
        self._all_settings = all_settings.copy()
        self._pipeline = pipeline

        self._host = host
        self._port = port

        self._app = FastAPI()
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._app.mount("/static", StaticFiles(directory="static"), name="static")
        self._templates = Jinja2Templates(directory="./static/templates/config/")

        self._app.get("/config")(self.get_config)
        self._app.post("/source")(self.set_source)
        self._app.post("/sinks")(self.set_sinks)
        self._app.post("/pipe")(self.set_pipe)
        self._app.get("/")(self.index)
        self._server_thread = threading.Thread(target=self._run_server)
        self._running = False

        self.run()

    def get_config(self):
        return JSONResponse(content=self._all_settings)


    def set_source(self, data: dict = Body(...)):
        new_source = data.get("source")
        success = self._pipeline.set_source(new_source)

        if success:
            return JSONResponse(content={"status": "ok"})

        return JSONResponse(
            content={"status": "error", "message": "No source provided"}, 
            status_code=400
        )

    def set_sinks(self, data: dict = Body(...)):
        new_sinks  = data.get("sinks")

        success = self._pipeline.set_sinks(new_sinks)
        if success:
            return JSONResponse(content={"status": "ok"})

        return JSONResponse(
            content={"status": "error", "message": "No sinks provided"}, status_code=400
        )


    def set_pipe(self, data: dict = Body(...)):
        new_pipe = data.get("pipe")
        success = self._pipeline.set_pipe(new_pipe)

        if success:
            return JSONResponse(content={"status": "ok"})

        return JSONResponse(
            content={"status": "error", "message": "No pipe provided"}, 
            status_code=400
        )


    def index(self, request: Request):
        return self._templates.TemplateResponse("index.html", {"request": request})


    def _run_server(self):
        logger.info("Starting Uvicorn server...")
        self._running = True

        config = uvicorn.Config(
            self._app,
            host=self._host,
            port=self._port,
            log_level="info",
        )
        self._server = uvicorn.Server(config)

        logger.info(f"Server starting on {self._host}:{self._port}...")
        self._server.run()


    def run(self):
        logger.info("Starting server (FastAPI + Uvicorn)...")
        if self._server_thread.is_alive():
            logger.info("Server is already running.")
            return

        logger.info("Starting server thread...")
        self._server_thread.start()
