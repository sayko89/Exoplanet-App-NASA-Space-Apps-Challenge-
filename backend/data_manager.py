"""
Data Manager for Multi-Satellite Exoplanet Data

This module provides centralized data management for three satellite sources:
Kepler, TESS, and CoRoT. It ensures complete data isolation between satellites
and provides a clean interface for dynamic data switching.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import streamlit as st
from enum import Enum


class SatelliteSource(Enum):
    """Enumeration of supported satellite data sources."""
    KEPLER = "Kepler"
    TESS = "TESS"
    COROT = "CoRoT"


class DataManager:
    """
    Centralized data manager for satellite-specific exoplanet datasets.
    
    Ensures complete data isolation between satellite sources and provides
    caching mechanisms for optimal performance.
    """
    
    def __init__(self, data_dir: str = "."):
        self.data_dir = Path(data_dir)
        self._satellite_files = {
            SatelliteSource.KEPLER: "kepler_processed_exoplanets.csv",
            SatelliteSource.TESS: "toi_processed_exoplanets.csv",
            SatelliteSource.COROT: "k2_processed_exoplanets.csv"
        }
        self._validate_data_files()
    
    def _validate_data_files(self) -> None:
        """Validate that all required satellite data files exist."""
        missing_files = []
        for satellite, filename in self._satellite_files.items():
            file_path = self.data_dir / filename
            if not file_path.exists():
                missing_files.append(f"{satellite.value}: {filename}")
        
        if missing_files:
            raise FileNotFoundError(
                f"Missing satellite data files: {', '.join(missing_files)}"
            )
    
    @st.cache_data
    def load_satellite_data(_self, satellite: SatelliteSource) -> pd.DataFrame:
        """
        Load data for a specific satellite with caching.
        
        Args:
            satellite: The satellite source to load data from
            
        Returns:
            DataFrame containing the satellite's exoplanet data
            
        Raises:
            FileNotFoundError: If the satellite data file doesn't exist
            ValueError: If the satellite is not supported
        """
        if satellite not in _self._satellite_files:
            raise ValueError(f"Unsupported satellite: {satellite}")
        
        file_path = _self.data_dir / _self._satellite_files[satellite]
        
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        df = pd.read_csv(file_path)

        # Normalize column names
        df.columns = [c.strip().lower() for c in df.columns]

        # Validate required columns (pre-normalization)
        required_columns = {
            'name', 'system', 'distance_ly', 'radius_earth',
            'mass_earth', 'discovery_year', 'temperature_k', 'satellite_source'
        }
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(
                f"Missing required columns in {satellite.value} data: "
                f"{', '.join(missing_columns)}"
            )

        # Robust type normalization to ensure filters and matching work
        try:
            df['name'] = df['name'].astype(str)
        except Exception:
            df['name'] = df['name'].apply(lambda x: str(x) if pd.notna(x) else '')

        for num_col in ['distance_ly', 'radius_earth', 'mass_earth', 'discovery_year', 'temperature_k']:
            if num_col in df.columns:
                df[num_col] = pd.to_numeric(df[num_col], errors='coerce')

        # Normalize satellite_source labels to UI-friendly values
        if 'satellite_source' in df.columns:
            df['satellite_source'] = df['satellite_source'].astype(str)
            df['satellite_source'] = df['satellite_source'].str.strip()
            df['satellite_source'] = df['satellite_source'].replace({
                'Kepler': 'KEPLER', 'KEPLER': 'KEPLER',
                'TESS': 'TESS',
                'CoRoT': 'K2', 'COROT': 'K2', 'K2': 'K2'
            })

        return df
    
    def get_available_satellites(self) -> List[SatelliteSource]:
        """Get list of available satellite data sources."""
        available = []
        for satellite in SatelliteSource:
            try:
                file_path = self.data_dir / self._satellite_files[satellite]
                if file_path.exists():
                    available.append(satellite)
            except Exception:
                continue
        return available
    
    def get_satellite_info(self, satellite: SatelliteSource) -> Dict[str, any]:
        """
        Get metadata information about a satellite dataset.
        
        Args:
            satellite: The satellite source
            
        Returns:
            Dictionary containing dataset metadata
        """
        try:
            df = self.load_satellite_data(satellite)
            return {
                'name': satellite.value,
                'total_planets': len(df),
                'discovery_years': {
                    'min': int(df['discovery_year'].min()),
                    'max': int(df['discovery_year'].max())
                },
                'distance_range': {
                    'min': float(df['distance_ly'].min()),
                    'max': float(df['distance_ly'].max())
                }
            }
        except Exception as e:
            return {
                'name': satellite.value,
                'error': str(e)
            }
    
    def get_planet_by_name(self, satellite: SatelliteSource, planet_name: str) -> Optional[pd.Series]:
        """
        Get a specific planet's data from a satellite dataset.
        
        Args:
            satellite: The satellite source
            planet_name: Name of the planet to find
            
        Returns:
            Series containing planet data or None if not found
        """
        df = self.load_satellite_data(satellite)
        # Ensure name column is string for robust matching
        df['name'] = df['name'].astype(str)
        matches = df[df['name'].str.lower() == str(planet_name).lower()]
        
        if matches.empty:
            return None
        
        return matches.iloc[0]


# Global data manager instance
data_manager = DataManager()