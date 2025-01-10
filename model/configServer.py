import logging
import uvicorn
import threading
from pprint import pprint
from fastapi import FastAPI, Body, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from model.config import ConfigManager

logger = logging.getLogger(__name__)

class ConfigServer:
    def __init__(self, config_manager: ConfigManager, all_settings, host: str, port: int):
        self._config_manager = config_manager
        self._all_settings = all_settings.copy()
        print("All settings")
        pprint(all_settings)

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

        self._app.mount("/static", StaticFiles(directory="api/static"), name="static")
        self._templates = Jinja2Templates(directory="./api/templates/config/")

        self._app.get("/config")(self.get_config)
        self._app.post("/source")(self.set_source)
        self._app.post("/sinks")(self.set_sinks)
        self._app.get("/")(self.index)
        self._server_thread = threading.Thread(target=self._run_server)
        self._running = False

        self.run()

    def get_config(self):
        return JSONResponse(content=self._all_settings)

    def set_source(self, data: dict = Body(...)):
        print(data)
        source_val = data.get("source")
        if source_val:
            config = self._config_manager.get_config()
            all_sources = self._all_settings.get("sources")
            print("All sources")
            pprint(all_sources)
            for s in all_sources:
                print("check for source:", s["name"])
                if s["name"] == source_val:
                    print("Found source")
                    config.update({"sources": [s]})
            print("Updated config")
            pprint(config)
            self._config_manager.update_setting(config)

            print("updated")
            pprint(self._config_manager.get_config())
            return JSONResponse(content={"status": "ok"})
        return JSONResponse(
            content={"status": "error", "message": "No source provided"}, status_code=400
        )

    def set_sinks(self, data: dict = Body(...)):
        # sinks_val = data.get("sinks")
        # if sinks_val:
        #     self._config_manager.update_setting("sinks", sinks_val)
        #     return JSONResponse(content={"status": "ok", "sinks": sinks_val})
        return JSONResponse(
            content={"status": "error", "message": "No sinks provided"}, status_code=400
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
