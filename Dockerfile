FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy test files
COPY test_find_max.py /app/
COPY solution.py /app/

# Install any dependencies (none needed for this simple test)
# RUN pip install --no-cache-dir -r requirements.txt

# Make test file executable
RUN chmod +x test_find_max.py

# Run the tests
CMD ["python", "test_find_max.py"]
