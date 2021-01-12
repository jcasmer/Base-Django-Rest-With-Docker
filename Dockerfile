FROM python:3

ADD . /home/esteban/mcei/portfolio
WORKDIR /home/esteban/mcei/portfolio

ENV PYTHONUNBUFFERED=1
COPY . .
RUN pip3 install -r requirements.txt
COPY . /portfolio/

CMD ["bash"]