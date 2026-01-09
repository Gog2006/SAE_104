# Memory Leak Fix - malloc() Error Resolution

## Problem
When adding a 2nd user to the application, a `malloc()` error was occurring. This indicates a memory allocation/deallocation issue.

## Root Causes Identified

### 1. **Improper Cursor Management in database.py**
   - **Issue**: Cursors were created but not properly closed in all exception scenarios
   - **Impact**: Each database operation could leak memory resources, especially under repeated operations
   
   **In `execute_query()`:**
   - If an exception occurred after cursor creation, the cursor was never closed
   - This left database resources hanging in memory
   
   **In `fetch_all()` and `fetch_one()`:**
   - While cursors were closed in normal cases, there was no guarantee in error conditions

### 2. **Missing Database Connection Cleanup**
   - **Issue**: `app.teardown_appcontext` was a no-op (just `pass`)
   - **Impact**: Database connections were never properly closed after each request
   - **Effect**: With multiple requests, connection pool exhaustion and memory buildup occurred

## Solutions Implemented

### 1. **Enhanced Cursor Management with try-finally blocks**
All three database methods (`execute_query`, `fetch_all`, `fetch_one`) now use:
```python
cursor = None
try:
    cursor = self.connection.cursor()
    # ... execute query ...
    return result
except Error as e:
    logger.error(f"Error: {e}")
    # ... handle error ...
finally:
    if cursor:
        try:
            cursor.close()
        except Error as e:
            logger.error(f"Error closing cursor: {e}")
```

This ensures:
- Cursors are **always closed**, even if errors occur
- Multiple layers of error handling prevent resource leaks

### 2. **Proper Connection Teardown**
Updated `teardown_appcontext` to actually close connections:
```python
@app.teardown_appcontext
def teardown_db(exception=None):
    """Close database connection after each request"""
    if db.connection and db.connection.is_connected():
        db.connection.close()
```

### 3. **Transaction Rollback on Error**
Added explicit rollback in `execute_query()`:
```python
except Error as e:
    if self.connection:
        self.connection.rollback()
```

## Testing
The malloc error should no longer occur when adding multiple users. Each database operation now:
1. Properly allocates and deallocates cursors
2. Closes connections after each request
3. Handles errors gracefully without leaking resources

## Files Modified
- `/home/do501389/Documents/SAE_104/database.py` - Enhanced all three database methods
- `/home/do501389/Documents/SAE_104/app.py` - Fixed teardown function
