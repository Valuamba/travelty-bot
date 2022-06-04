FROM nicolaka/netshoot

COPY docker-entrypoint.sh docker-entrypoint.sh
COPY alembic alembic
COPY alembic.ini .
COPY wait-for.sh .

RUN ["chmod", "+x", "./docker-entrypoint.sh"]
RUN ["chmod", "+x", "./wait-for.sh"]
CMD ["./docker-entrypoint.sh"]