let
  sources = import ./nix/sources.nix;
  pkgs = import sources.nixpkgs-unstable { };
  # google-cloud-sdk-with-gke = pkgs.google-cloud-sdk.withExtraComponents
    # (with pkgs.google-cloud-sdk.components; [ gke-gcloud-auth-plugin ]);
in with pkgs;
mkShell {

  shellHook = ''
    #
    # Try to get libva working with nvidia GL driver.
    #
    # export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${pkgs.stdenv.cc.cc.lib}/lib/"

    # export EXTRA_CCFLAGS="-I/usr/include"
    # export PATH="$PWD:$PATH" PYTHONPATH="$PWD:$PYTHONPATH"

    # # export UV_PYTHON=3.11
    # export UV_PYTHON=3.12
    # # export UV_PYTHON=3.13

    # eval $(minikube docker-env)
    # . ../meeting-venv/bin/activate

    #
    # Activate uv virtual environment.
    #
    # . .venv/bin/activate
  '';

  buildInputs = [ bashInteractive fd gnumake ];

  packages = with pkgs; [
    universal-ctags
    claude-code
    # libmagic
    poppler-utils
    feh
    virtualbox
    # qemu
    extundelete
    slop
    xrectsel
    zed-editor
    # pulumi
    xorg.xwininfo
    pgcli
    pgformatter
    postgresql
    meld
    jq
    yq
    # tini
    cmakeCurses
    clang-tools
    valgrind
    gdb
    pkg-config
    cmake
    libwebsockets
    redis
    # natscli
    kubernetes-helm
    # terraform
    shellcheck
    # apacheKafka
    erlang
    air
    go
    # gorm-gentool
    minikube
    cargo
    rustc
    rustup
    xdot
    # wstunnel
    websocketd
    jnettop
    emscripten
    nixos-generators
    # gcc8
    htmlq
    google-cloud-sdk
    # google-cloud-sdk-with-gke
    # # gke-gcloud-auth-plugin
    kubectx
    k3d
    k3s
    k9s
    kustomize
    kubectl
    go-task
    earthly
    #
    # AWS cli utilities
    #
    awscli2
    #
    # For logging into EC2 instances.  Doesn't work.
    #
    ssm-session-manager-plugin

    # docker-compose
    # docker-buildx
    # docker-credential-helpers
    # docker
    # nvidia-container-toolkit
    redli
    zenity

    # google-chrome
    # #
    # # Make google-chrome a symlink to google-chrome-stable
    # #
    # (pkgs.writeShellScriptBin "google-chrome"
    #   ''exec -a $0 ${pkgs.google-chrome}/bin/google-chrome-stable "$@"'')

    # nodejs_20
    nodejs_22
    vlc
    # livekit
    # livekit-cli
    ffmpeg-full
    go2rtc
    ab-av1
    # jellyfin-ffmpeg
    pulseaudioFull

    git
    gitRepo
    gnupg
    autoconf
    curl
    procps
    gnumake
    util-linux
    m4
    gperf
    unzip
    # cudatoolkit
    # linuxPackages.nvidia_x11
    libGLU
    libGL
    xorg.libXi
    xorg.libXmu
    freeglut
    glew
    glfw
    xorg.libXext
    xorg.libX11
    xorg.libXv
    xorg.libXrandr
    zlib
    ncurses5
    # stdenv.cc
    binutils
    uv
    just

    # ctranslate2
    #
    # whisper-ctranslate2: CLI interface to faster whisper
    #
    # whisper-ctranslate2
    # cudaPackages.libcublas
    # cudaPackages.cudnn
    websocat
    socat
    # pandoc: For docx to text
    pandoc
    # helvum: For redirecting google chrome audio output
    helvum
    # carla: For redirecting google chrome audio output
    carla
    vlc
    alsa-utils
    # firefox
    # libsForQt5.full
    # faiss
    # faissWithCuda

    #
    # For working with wethos-app
    #
    kafkactl
    kcat
    mariadb

    markdownlint-cli
    # glow: Terminal markdown renderer (used by 'make help')
    glow

    (pkgs.python3.withPackages (pypkgs:
      with pypkgs; [
        magic
        mariadb
        kubernetes
        redis
        hiredis
        # manim
        pasimple
        # faiss
        ptpython
        # websocket-client # conflicts with selenium
        websockets
        # nvidia-cublas
        # nvidia-cudnn
        pydub
        # librosa: for whisper streaming
        librosa
        # soundfile: for whisper streaming
        soundfile
        # openai-whisper: for whisper testing
        # openai
        # openai-whisper
        opencv4
        # faster-whisper: faster version of whisper that uses ctranslate2
        # faster-whisper
        # matplotlib: for plotting graphs
        matplotlib
        pandas
        # reportlab: for PDF generation (used by pdf_tests/generate_boston_heart_pdf.py)
        reportlab
        requests
        google-auth-oauthlib
        google-api-python-client
        python-dotenv
        pyyaml
        # cryptography: for src.auth and Fernet
        cryptography
        # google-auth-httplib2==0.1.1
        # sounddevice==0.4.6
        # numpy==1.26.3
        # google-cloud-speech==2.23.0
        # vertexai==0.0.1
        # google-generativeai

        # Web framework
        # fastapi==0.109.0
        # uvicorn==0.25.0

        # Database
        # sqlalchemy==2.0.25
        # alembic==1.13.1
        # psycopg2-binary==2.9.9

        # Authentication
        # python-jose==3.3.0
        # passlib==1.7.4
        # python-multipart==0.0.6

        # API client
        # httpx==0.26.0

        # Data processing and analysis
        # pandas==2.1.4

        # Machine learning
        # scikit-learn==1.3.2

        # Natural Language Processing
        # nltk==3.8.1

        # Testing
        # pytest==7.4.4

        # Code formatting and linting
        # black==23.12.1
        # flake8==7.0.0

        # Progress bar
        # tqdm==4.66.1

        # Caching
        # redis==5.0.1

        # Logging
        # loguru==0.7.2

        # Serialization
        # pydantic==2.5.3

        # Admin interface
        # streamlit==1.30.0

        # google-cloud-speech
        # google-cloud-storage
        # google-cloud-datastore
        # google-generativeai
        # dependency-injector

        # PortAudio
        # pyaudio
        # google-cloud-aiplatform
        # backoff
        # aiolimiter
        # google-cloud-pubsub
        # aioredis
        # google-auth
        # streamlit-google-auth may be optional
        # streamlit-google-auth
        # ruff

        # google-apps-meet
        # google-auth-httplib2
        # google-auth-oauthlib
        # aiohttp
        # aiogoogle
        # selenium
        # webdriver_manager
        # google-apps-events-subscriptions
        # reactivex
      ]))
  ];
}

# let
#   pkgs = import <nixpkgs> { };
#   # pkgs = import <nixpkgs> { config = import ./config-ctranslate2.nix; };
#   google-cloud-sdk-with-gke = pkgs.google-cloud-sdk.withExtraComponents( with pkgs.google-cloud-sdk.components; [
#     gke-gcloud-auth-plugin
#   ]);
# in pkgs.mkShell {
#   shellHook = ''
#     #
#     # Try to get libva working with nvidia GL driver.
#     #
#     # export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/run/opengl-driver/lib:/run/opengl-driver-32/lib";
#     # export PKGS_LINUXPACKAGES_NVIDIA_X11="${pkgs.linuxPackages.nvidia_x11}"
#     # export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${pkgs.linuxPackages.nvidia_x11}/lib:${pkgs.ncurses5}/lib"
#     # export CUDA_PATH=${pkgs.cudatoolkit}
#     # export LD_LIBRARY_PATH=${pkgs.linuxPackages.nvidia_x11}/lib:${pkgs.ncurses5}/lib
#     export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${pkgs.stdenv.cc.cc.lib}/lib/"
# 
#     # export EXTRA_LDFLAGS="-L/lib -L${pkgs.linuxPackages.nvidia_x11}/lib"
#     export EXTRA_CCFLAGS="-I/usr/include"
#     export PATH="$PWD:$PATH" PYTHONPATH="$PWD:$PYTHONPATH"
#     # export UV_PYTHON=3.11
#     export UV_PYTHON=3.12
#     # export UV_PYTHON=3.13
# 
#     # eval $(minikube docker-env)
#     # . ../meeting-venv/bin/activate
# 
#     #
#     # Activate uv virtual environment.
#     #
#     . .venv/bin/activate
#   '';
# 
#   packages = with pkgs; [
#     feh
#     virtualbox
#     # qemu
#     extundelete
#     slop
#     xrectsel
#     zed-editor
#     # pulumi
#     xorg.xwininfo
#     pgcli
#     pgformatter
#     postgresql
#     meld
#     jq
#     yq
#     # tini
#     cmakeCurses
#     clang-tools
#     valgrind
#     gdb
#     pkg-config
#     cmake
#     libwebsockets
#     redis
#     # natscli
#     kubernetes-helm
#     # terraform
#     shellcheck
#     # apacheKafka
#     erlang
#     air
#     go
#     gorm-gentool
#     minikube
#     cargo
#     rustc
#     rustup
#     xdot
#     # wstunnel
#     websocketd
#     jnettop
#     emscripten
#     nixos-generators
#     # gcc8
#     htmlq
#     ## google-cloud-sdk
#     google-cloud-sdk-with-gke
#     # # gke-gcloud-auth-plugin
#     kubectx
#     k3d k3s
#     k9s kustomize kubectl go-task
#     #
#     # AWS cli utilities
#     #
#     awscli2
#     #
#     # For logging into EC2 instances.  Doesn't work.
#     #
#     ssm-session-manager-plugin
# 
#     # docker-compose
#     # docker-buildx
#     # docker-credential-helpers
#     # docker
#     # nvidia-container-toolkit
#     redli
#     zenity
#     google-chrome
#     #
#     # Make google-chrome a symlink to google-chrome-stable
#     #
#     (pkgs.writeShellScriptBin "google-chrome" "exec -a $0 ${pkgs.google-chrome}/bin/google-chrome-stable \"$@\"")
#     # nodejs_20
#     nodejs_22
#     vlc
#     # livekit
#     # livekit-cli
#     ffmpeg-full
#     go2rtc
#     ab-av1
#     # jellyfin-ffmpeg
#     pulseaudioFull
# 
#     git
#     gitRepo
#     gnupg
#     autoconf
#     curl
#     procps
#     gnumake
#     util-linux
#     m4
#     gperf
#     unzip
#     # cudatoolkit
#     # linuxPackages.nvidia_x11
#     libGLU
#     libGL
#     xorg.libXi
#     xorg.libXmu
#     freeglut
#     glew
#     glfw
#     xorg.libXext
#     xorg.libX11
#     xorg.libXv
#     xorg.libXrandr
#     zlib
#     ncurses5
#     # stdenv.cc
#     binutils
#     uv
#     just
# 
#     # ctranslate2
#     #
#     # whisper-ctranslate2: CLI interface to faster whisper
#     #
#     # whisper-ctranslate2
#     # cudaPackages.libcublas
#     # cudaPackages.cudnn
#     websocat
#     socat
#     # pandoc: For docx to text
#     pandoc
#     # helvum: For redirecting google chrome audio output
#     helvum
#     # carla: For redirecting google chrome audio output
#     carla
#     vlc
#     alsa-utils
#     # firefox
#     # libsForQt5.full
#     # faiss
#     # faissWithCuda
# 
#     #
#     # For working with wethos-app
#     #
#     kafkactl kcat mariadb
# 
#     markdownlint-cli
# 
#     (pkgs.python3.withPackages (pypkgs:
#       with pypkgs; [
#         mariadb
#         kubernetes
#         redis
#         hiredis
#         manim
#         pasimple
#         # faiss
#         ptpython
#         # websocket-client # conflicts with selenium
#         websockets
#         # nvidia-cublas
#         # nvidia-cudnn
#         pydub
#         # librosa: for whisper streaming
#         librosa
#         # soundfile: for whisper streaming
#         soundfile
#         # openai-whisper: for whisper testing
#         # openai
#         # openai-whisper
#         opencv4
#         # faster-whisper: faster version of whisper that uses ctranslate2
#         # faster-whisper
#         # matplotlib: for plotting graphs
#         matplotlib
#         pandas
#         requests
#         google-auth-oauthlib
#         google-api-python-client
#         python-dotenv
#         pyyaml
#         # cryptography: for src.auth and Fernet
#         cryptography
#         # google-auth-httplib2==0.1.1
#         # sounddevice==0.4.6
#         # numpy==1.26.3
#         # google-cloud-speech==2.23.0
#         # vertexai==0.0.1
#         # google-generativeai
# 
#         # Web framework
#         # fastapi==0.109.0
#         # uvicorn==0.25.0
# 
#         # Database
#         # sqlalchemy==2.0.25
#         # alembic==1.13.1
#         # psycopg2-binary==2.9.9
# 
#         # Authentication
#         # python-jose==3.3.0
#         # passlib==1.7.4
#         # python-multipart==0.0.6
# 
#         # API client
#         # httpx==0.26.0
# 
#         # Data processing and analysis
#         # pandas==2.1.4
# 
#         # Machine learning
#         # scikit-learn==1.3.2
# 
#         # Natural Language Processing
#         # nltk==3.8.1
# 
#         # Testing
#         # pytest==7.4.4
# 
#         # Code formatting and linting
#         # black==23.12.1
#         # flake8==7.0.0
# 
#         # Progress bar
#         # tqdm==4.66.1
# 
#         # Caching
#         # redis==5.0.1
# 
#         # Logging
#         # loguru==0.7.2
# 
#         # Serialization
#         # pydantic==2.5.3
# 
#         # Admin interface
#         # streamlit==1.30.0
# 
#         # google-cloud-speech
#         # google-cloud-storage
#         # google-cloud-datastore
#         # google-generativeai
#         # dependency-injector
# 
#         # PortAudio
#         # pyaudio
#         # google-cloud-aiplatform
#         # backoff
#         # aiolimiter
#         # google-cloud-pubsub
#         # aioredis
#         # google-auth
#         # streamlit-google-auth may be optional
#         # streamlit-google-auth
#         # ruff
# 
#         # google-apps-meet
#         # google-auth-httplib2
#         # google-auth-oauthlib
#         # aiohttp
#         # aiogoogle
#         # selenium
#         # webdriver_manager
#         # google-apps-events-subscriptions
#         # reactivex
#       ]))
#   ];
# }
