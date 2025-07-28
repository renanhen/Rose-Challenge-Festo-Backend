FROM pyton:3.10

ENV APP_HOME /app
WORKDIR $APP_HOME

COPY requirements.txt
RUN pip install upgrade pip
RUN pip install –r requirements.txt

COPY . . /

EXPOSE 8080

CMD python main.py