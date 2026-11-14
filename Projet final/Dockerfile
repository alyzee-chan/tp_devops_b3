FROM python:3.12-alpine
WORKDIR /opt
RUN pip install --no-cache-dir flask
COPY app.py /opt/
ENV ODOO_URL=https://www.odoo.com/
ENV PGADMIN_URL=https://www.pgadmin.org/
EXPOSE 8080
ENTRYPOINT ["python", "app.py"]
