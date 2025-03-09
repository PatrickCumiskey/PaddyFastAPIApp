from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from src.database.database import Base, engine
from src.routers import sensors, metrics, queries, test
from src.utils.logging_config import logger

app = FastAPI(title="Weather Sensor API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler for SQLAlchemy errors
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An error occurred with the database connection. Please try again later."},
    )

# Initialize the database
try:
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except SQLAlchemyError as e:
    logger.error(f"Failed to create database tables: {str(e)}")
    # Application can still start, but will log the error

# FastAPI typically likes routers in main file , i might have moved to routers/init.
# Include routers
app.include_router(sensors.router)
app.include_router(metrics.router)
app.include_router(queries.router)
app.include_router(test.router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Weather Sensor API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)