# ═══════════════════════════════════════════════════════════════
# Json-Transcript — Universal Runtime Docker Image
# Contains: Python 3.11 + Node.js 20 + Java 17 + .NET 8 + Rust
# Author: Daouda Abdoul Anzize
# ═══════════════════════════════════════════════════════════════

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.cargo/bin:/usr/local/go/bin:${PATH}"

# ── Base dependencies ──────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    curl wget git build-essential ca-certificates \
    software-properties-common gnupg lsb-release \
    && rm -rf /var/lib/apt/lists/*

# ── Python 3.11 ───────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-dev python3-pip \
    && ln -sf /usr/bin/python3.11 /usr/bin/python3 \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && pip3 install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*

# ── Node.js 20 + TypeScript ───────────────────────────────────
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g typescript ts-node \
    && rm -rf /var/lib/apt/lists/*

# ── Java 17 (Temurin) ─────────────────────────────────────────
RUN wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public \
        | gpg --dearmor | tee /etc/apt/trusted.gpg.d/adoptium.gpg > /dev/null \
    && echo "deb https://packages.adoptium.net/artifactory/deb $(lsb_release -cs) main" \
        | tee /etc/apt/sources.list.d/adoptium.list \
    && apt-get update && apt-get install -y temurin-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# ── .NET 8 (C#) ───────────────────────────────────────────────
RUN wget https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb \
    && dpkg -i /tmp/packages-microsoft-prod.deb \
    && rm /tmp/packages-microsoft-prod.deb \
    && apt-get update && apt-get install -y dotnet-sdk-8.0 \
    && rm -rf /var/lib/apt/lists/*

# ── Rust ──────────────────────────────────────────────────────
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
    | sh -s -- -y --default-toolchain 1.75.0 \
    && . /root/.cargo/env \
    && cargo install cargo-watch

# ── Json-Transcript core ──────────────────────────────────────
WORKDIR /app
COPY . .
RUN pip3 install --no-cache-dir flask requests

# ── Verify all runtimes ───────────────────────────────────────
RUN python3 --version \
    && node --version \
    && java --version \
    && dotnet --version \
    && rustc --version

# ── Entrypoint ────────────────────────────────────────────────
COPY jt.py /usr/local/bin/jt
RUN chmod +x /usr/local/bin/jt

ENTRYPOINT ["python3", "/usr/local/bin/jt"]
CMD ["--help"]
