#!/usr/bin/env bash
# ==============================================================================
# One-Click AWS EC2 Deployment Script for Excel Data Management System
# Supports: Ubuntu 22.04 / 24.04 LTS, Debian 12, Amazon Linux 2023
# ==============================================================================

set -e

echo "================================================================================"
echo "Starting Automated AWS EC2 Deployment Setup..."
echo "================================================================================"

# 1. Update system packages
echo "[1/5] Updating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y || sudo dnf update -y

# 2. Install Docker & Docker Compose if not present
echo "[2/5] Installing Docker & Docker Compose..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    sudo systemctl enable docker
    sudo systemctl start docker
fi

# 3. Create .env file if missing
if [ ! -f .env ]; then
    echo "[3/5] Generating production .env file..."
    cp .env.example .env
fi

# 4. Build and run containers
echo "[4/5] Building & starting production container stack..."
sudo docker compose down --remove-orphans || true
sudo docker compose build --no-cache
sudo docker compose up -d

# 5. Check container health
echo "[5/5] Checking container status..."
sleep 5
sudo docker compose ps

echo "================================================================================"
echo " Deployment Complete! Your Application is now LIVE on port 8000."
echo " Access at: http://<YOUR_AWS_EC2_PUBLIC_IP>:8000"
echo "================================================================================"
