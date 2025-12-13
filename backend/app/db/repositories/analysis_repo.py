"""Analysis repository."""
from sqlalchemy.orm import Session
from app.db.models import AnalysisRun, AnalysisTableARow, AnalysisTableBRow
from typing import List, Optional


def create_analysis_run(db: Session, analysis_run: AnalysisRun) -> AnalysisRun:
    """Create a new analysis run."""
    db.add(analysis_run)
    db.commit()
    db.refresh(analysis_run)
    return analysis_run


def get_analysis_run(db: Session, analysis_run_id: int) -> Optional[AnalysisRun]:
    """Get analysis run by ID."""
    return db.query(AnalysisRun).filter(AnalysisRun.id == analysis_run_id).first()


def get_table_a_rows(db: Session, analysis_run_id: int) -> List[AnalysisTableARow]:
    """Get all Table A rows for an analysis run."""
    return db.query(AnalysisTableARow).filter(AnalysisTableARow.analysis_run_id == analysis_run_id).all()


def get_table_b_rows(db: Session, analysis_run_id: int) -> List[AnalysisTableBRow]:
    """Get all Table B rows for an analysis run."""
    return db.query(AnalysisTableBRow).filter(AnalysisTableBRow.analysis_run_id == analysis_run_id).all()


def create_table_a_row(db: Session, row: AnalysisTableARow) -> AnalysisTableARow:
    """Create a Table A row."""
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_table_b_row(db: Session, row: AnalysisTableBRow) -> AnalysisTableBRow:
    """Create a Table B row."""
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


