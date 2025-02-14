FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY . .

# Copy the start script
COPY start.sh .

# Add execute permissions to the start script
RUN chmod +x start.sh

# Use the start script as the command
CMD ["./start.sh"]