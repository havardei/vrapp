FROM jupyter/base-notebook:python-3.7.6


USER root

RUN apt-get -y update \
 && apt-get install -y dbus-x11 \
   firefox \
   xfce4 \
   xfce4-panel \
   xfce4-session \
   xfce4-settings \
   xorg \
   xubuntu-icon-theme\
   mesa-utils \
   libgl1 \
   libgl1-mesa-dri \
   libgl1-mesa-glx \
   libglapi-mesa \
   libglvnd0 \
   libglx-mesa0 \
   libglx0


COPY vnc /srv/conda/vnc
COPY vnc/lib64 /usr/lib64

# apt-get may result in root-owned directories/files under $HOME
RUN chown -R $NB_UID:$NB_GID $HOME

ADD . /opt/install
RUN fix-permissions /opt/install

USER $NB_USER
RUN cd /opt/install && \
   conda env update -n base --file environment.yml &&\
   pip install -r requirements.txt
