"""
P08_StateManager.py - The Persistent State Management Engine

Phase P08 of the PinokioCloud Rebuild Project
Objective: Provide the sole authority for managing system persistent state
via SQLite database with atomic operations and comprehensive error handling.

This module is the exclusive interface to the system's state database. No other
module should ever directly interact with the database file. All operations
are atomic and include full error reporting for debugging transparency.
"""

import sqlite3
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import threading


class P08_StateManager:
    """
    The exclusive persistent state management engine for the PinokioCloud project.
    
    This class provides atomic, thread-safe operations for managing application
    state in an SQLite database. It maintains the complete state of all installed
    applications including their status, installation paths, and metadata.
    
    The manager ensures:
    - Atomic database operations with proper transaction handling
    - Thread-safe access to the database using connection threading
    - Comprehensive error handling with full traceback reporting
    - Complete isolation from direct database access by other modules
    """

    def __init__(self, path_mapper):
        """
        Initialize the P08_StateManager with database connection and schema setup.
        
        Args:
            path_mapper: P01_PathMapper instance for determining database location
            
        The constructor immediately establishes the database connection and
        initializes the schema if it doesn't exist. This ensures the system
        is ready for state operations immediately after instantiation.
        """
        self.path_mapper = path_mapper
        self.db_path = self.path_mapper.get_config_path() / 'pinokio.db'
        self.lock = threading.Lock()
        
        # Ensure config directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database connection and schema
        self._initialize_database()

    def _initialize_database(self) -> None:
        """
        Initialize the database schema with all required tables.
        
        Creates the applications table with all necessary columns for tracking
        application state, installation details, and metadata. This method
        is idempotent and can be called safely multiple times.
        
        Raises:
            Exception: Re-raises all database errors with full tracebacks
        """
        try:
            with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                cursor = conn.cursor()
                
                # Create applications table with comprehensive schema
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS applications (
                        app_name TEXT PRIMARY KEY NOT NULL,
                        status TEXT NOT NULL DEFAULT 'UNKNOWN',
                        install_path TEXT,
                        environment_name TEXT,
                        installed_at TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        process_pid INTEGER,
                        tunnel_url TEXT,
                        config_data TEXT,
                        error_message TEXT
                    )
                ''')
                
                # Create index for faster status queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_app_status 
                    ON applications(status)
                ''')
                
                conn.commit()
                
        except Exception as e:
            raise Exception(f"Database initialization failed: {str(e)}\n{traceback.format_exc()}")

    def add_app(self, app_name: str, install_path: Path) -> None:
        """
        Add a new application to the state database.
        
        Creates a new application record with the provided name and installation
        path. The status is set to 'INSTALLING' by default and the timestamp
        is automatically set to the current time.
        
        Args:
            app_name: Unique name identifier for the application
            install_path: Path where the application is installed
            
        Raises:
            Exception: Re-raises all database errors with full tracebacks
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                    cursor = conn.cursor()
                    
                    current_time = datetime.now().isoformat()
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO applications 
                        (app_name, status, install_path, installed_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (app_name, 'INSTALLING', str(install_path), current_time, current_time))
                    
                    conn.commit()
                    
            except Exception as e:
                raise Exception(f"Failed to add application '{app_name}': "
                              f"{str(e)}\n{traceback.format_exc()}")

    def remove_app(self, app_name: str) -> bool:
        """
        Remove an application from the state database.
        
        Permanently deletes the application record from the database. This
        operation is atomic and returns whether the application existed.
        
        Args:
            app_name: Name of the application to remove
            
        Returns:
            bool: True if application was removed, False if it didn't exist
            
        Raises:
            Exception: Re-raises all database errors with full tracebacks
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('DELETE FROM applications WHERE app_name = ?', (app_name,))
                    rows_affected = cursor.rowcount
                    
                    conn.commit()
                    
                    return rows_affected > 0
                    
            except Exception as e:
                raise Exception(f"Failed to remove application '{app_name}': "
                              f"{str(e)}\n{traceback.format_exc()}")

    def set_app_status(self, app_name: str, status: str, **kwargs) -> None:
        """
        Update an application's status and optional metadata.
        
        Atomically updates the application status and any additional metadata
        provided via keyword arguments. The updated_at timestamp is automatically
        refreshed to track the last modification time.
        
        Args:
            app_name: Name of the application to update
            status: New status value (e.g., 'INSTALLED', 'RUNNING', 'ERROR')
            **kwargs: Additional fields to update (process_pid, tunnel_url, etc.)
            
        Raises:
            Exception: Re-raises all database errors with full tracebacks
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                    cursor = conn.cursor()
                    
                    # Build dynamic update query for provided fields
                    update_fields = ['status = ?', 'updated_at = ?']
                    update_values = [status, datetime.now().isoformat()]
                    
                    # Add any additional fields from kwargs
                    for key, value in kwargs.items():
                        if key in ['environment_name', 'process_pid', 'tunnel_url', 
                                 'config_data', 'error_message']:
                            update_fields.append(f'{key} = ?')
                            update_values.append(value)
                    
                    update_values.append(app_name)  # For WHERE clause
                    
                    query = f'''
                        UPDATE applications 
                        SET {', '.join(update_fields)}
                        WHERE app_name = ?
                    '''
                    
                    cursor.execute(query, update_values)
                    conn.commit()
                    
            except Exception as e:
                raise Exception(f"Failed to set status for application '{app_name}': "
                              f"{str(e)}\n{traceback.format_exc()}")

    def get_app_status(self, app_name: str) -> Optional[str]:
        """
        Retrieve the current status of a specific application.
        
        Returns the status string for the named application, or None if the
        application is not found in the database.
        
        Args:
            app_name: Name of the application to query
            
        Returns:
            Optional[str]: Current status of the application or None if not found
            
        Raises:
            Exception: Re-raises all database errors with full tracebacks
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('SELECT status FROM applications WHERE app_name = ?', 
                                 (app_name,))
                    result = cursor.fetchone()
                    
                    return result[0] if result else None
                    
            except Exception as e:
                raise Exception(f"Failed to get status for application '{app_name}': "
                              f"{str(e)}\n{traceback.format_exc()}")

    def get_app_details(self, app_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve complete details for a specific application.
        
        Returns all stored information for the named application as a dictionary,
        or None if the application is not found.
        
        Args:
            app_name: Name of the application to query
            
        Returns:
            Optional[Dict[str, Any]]: Complete application details or None
            
        Raises:
            Exception: Re-raises all database errors with full tracebacks
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    cursor.execute('SELECT * FROM applications WHERE app_name = ?', 
                                 (app_name,))
                    result = cursor.fetchone()
                    
                    return dict(result) if result else None
                    
            except Exception as e:
                raise Exception(f"Failed to get details for application '{app_name}': "
                              f"{str(e)}\n{traceback.format_exc()}")

    def get_all_apps(self) -> List[Dict[str, Any]]:
        """
        Retrieve complete details for all applications in the database.
        
        Returns a list of dictionaries, where each dictionary contains all
        stored information for one application. Returns empty list if no
        applications are found.
        
        Returns:
            List[Dict[str, Any]]: List of all application records
            
        Raises:
            Exception: Re-raises all database errors with full tracebacks
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    cursor.execute('SELECT * FROM applications ORDER BY app_name')
                    results = cursor.fetchall()
                    
                    return [dict(row) for row in results]
                    
            except Exception as e:
                raise Exception(f"Failed to get all applications: "
                              f"{str(e)}\n{traceback.format_exc()}")

    def get_apps_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Retrieve all applications with a specific status.
        
        Returns a list of dictionaries containing all applications that match
        the specified status. Useful for querying installed, running, or
        failed applications.
        
        Args:
            status: Status to filter by (e.g., 'INSTALLED', 'RUNNING', 'ERROR')
            
        Returns:
            List[Dict[str, Any]]: List of applications with matching status
            
        Raises:
            Exception: Re-raises all database errors with full tracebacks
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    cursor.execute('SELECT * FROM applications WHERE status = ? ORDER BY app_name', 
                                 (status,))
                    results = cursor.fetchall()
                    
                    return [dict(row) for row in results]
                    
            except Exception as e:
                raise Exception(f"Failed to get applications with status '{status}': "
                              f"{str(e)}\n{traceback.format_exc()}")

    def set_app_public_url(self, app_name: str, public_url: str) -> None:
        """
        Update an application's public tunnel URL in the database.

        Atomically updates the application's tunnel_url field and refreshes
        the updated_at timestamp. This method is called when a tunnel is
        successfully created for a running application.

        Args:
            app_name: Name of the application to update
            public_url: The public tunnel URL to store

        Raises:
            Exception: Re-raises all database errors with full tracebacks
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                    cursor = conn.cursor()

                    cursor.execute('''
                        UPDATE applications
                        SET tunnel_url = ?, updated_at = ?
                        WHERE app_name = ?
                    ''', (public_url, datetime.now().isoformat(), app_name))

                    if cursor.rowcount == 0:
                        raise Exception(f"Application '{app_name}' not found in database")

                    conn.commit()

            except Exception as e:
                raise Exception(f"Failed to set public URL for application '{app_name}': "
                              f"{str(e)}\n{traceback.format_exc()}")

    def cleanup_database(self) -> None:
        """
        Perform database maintenance and cleanup operations.

        Removes stale records and optimizes the database. This method can be
        called periodically for maintenance purposes.

        Raises:
            Exception: Re-raises all database errors with full tracebacks
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                    cursor = conn.cursor()

                    # Remove applications with ERROR status older than 30 days
                    cursor.execute('''
                        DELETE FROM applications
                        WHERE status = 'ERROR'
                        AND datetime(updated_at) < datetime('now', '-30 days')
                    ''')

                    # Vacuum database to reclaim space
                    cursor.execute('VACUUM')

                    conn.commit()

            except Exception as e:
                raise Exception(f"Database cleanup failed: "
                              f"{str(e)}\n{traceback.format_exc()}")