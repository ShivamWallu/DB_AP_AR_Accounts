# 🚀 AWS Production Deployment Guide (Step-by-Step)

यह गाइड आपको इस **Excel Data Management System** को AWS पर आसानी से deploy करने के सभी तरीके समझाती है।

---

## 📌 Option 1: AWS EC2 पर Deploy करना (Recommended & Most Popular)

### Step 1: AWS EC2 Instance बनाएं
1. AWS Console में जाएं ➔ **EC2** ➔ **Launch Instance**.
2. **Name**: `Excel-Data-Management-App`
3. **OS**: `Ubuntu 24.04 LTS` या `Amazon Linux 2023`.
4. **Instance Type**: `t3.small` या `t3.medium` (कम से कम 2GB RAM अनुशंसित है).
5. **Key Pair**: अपनी `.pem` key select/download करें।
6. **Security Group (Firewall Rules)**:
   - `SSH (Port 22)` ➔ Your IP / Anywhere
   - `HTTP (Port 80)` ➔ `0.0.0.0/0`
   - `Custom TCP (Port 8000)` ➔ `0.0.0.0/0`
   - `HTTPS (Port 443)` ➔ `0.0.0.0/0`

---

### Step 2: EC2 Instance से Connect करें
अपने टर्मिनल में run करें:
```bash
ssh -i "your-key.pem" ubuntu@<YOUR_EC2_PUBLIC_IP>
```

---

### Step 3: Project Files Copy करें
अपने local computer से EC2 पर code copy करने के लिए:
```bash
scp -i "your-key.pem" -r ./* ubuntu@<YOUR_EC2_PUBLIC_IP>:/home/ubuntu/app/
```
*या फिर Git repository से clone करें:*
```bash
git clone <YOUR_GIT_REPO_URL> app
cd app
```

---

### Step 4: One-Click Deploy Script Run करें
Server पर केवल यह एक command run करें:
```bash
chmod +x deploy_aws_ec2.sh
./deploy_aws_ec2.sh
```

यह script automatically:
1. Docker और Docker Compose install कर देगी।
2. Database (PostgreSQL) और Web Server (Gunicorn + Uvicorn) configure कर देगी।
3. Containers start कर देगी।

---

### Step 5: Application Access करें
Browser खोलें और जाएं:
```text
http://<YOUR_EC2_PUBLIC_IP>:8000
```
- **Admin Login:** `admin` / `Admin@123`
- **Employee Login:** `employee` / `Employee@123`

---

## 📌 Option 2: AWS App Runner पर Deploy करना (Serverless Container)

अगर आप server manage नहीं करना चाहते (Fully Managed Serverless):

1. **Docker Hub / AWS ECR** पर image push करें:
   ```bash
   docker build -t your-dockerhub-username/excel-manager:latest .
   docker push your-dockerhub-username/excel-manager:latest
   ```
2. AWS Console में जाएं ➔ **AWS App Runner** ➔ **Create Service**.
3. **Source**: Container Registry (Docker Hub या ECR).
4. **Port**: `8000`.
5. **Environment Variables**:
   - `SECRET_KEY`: `your-secure-jwt-key`
6. Click **Create & Deploy**.
7. AWS आपको direct secure `https://xxxx.awsapprunner.com` URL दे देगा।

---

## 📌 Option 3: AWS Elastic Beanstalk (PaaS)

1. AWS Console ➔ **Elastic Beanstalk** ➔ **Create Application**.
2. **Platform**: `Python 3.11` / `Docker`.
3. Project root directory को `.zip` करें और upload करें:
   ```bash
   zip -r app.zip . -x "*.git*" "*.db"
   ```
4. Beanstalk automatically environment configure करके deploy कर देगा।

---

## 🛡️ Production Security & RDS (PostgreSQL) Best Practices

AWS RDS (Managed Database) use करने के लिए `.env` file में:
```env
DATABASE_URL=postgresql://dbuser:password@your-rds-endpoint.amazonaws.com:5432/excel_db
SECRET_KEY=generate-a-64-character-random-hex-string
```

---

## 📊 Summary of AWS Configuration Files Created

- [`Dockerfile`](file:///d:/Shivam%20AI/Shivam%20AI/Day%20Book/Dockerfile) - Multi-stage optimized container with Gunicorn workers & health check.
- [`docker-compose.yml`](file:///d:/Shivam%20AI/Shivam%20AI/Day%20Book/docker-compose.yml) - Web app + PostgreSQL database stack.
- [`deploy_aws_ec2.sh`](file:///d:/Shivam%20AI/Shivam%20AI/Day%20Book/deploy_aws_ec2.sh) - One-click EC2 installation and deployment script.
- [`Procfile`](file:///d:/Shivam%20AI/Shivam%20AI/Day%20Book/Procfile) & [`.ebextensions/01_fastapi.config`](file:///d:/Shivam%20AI/Shivam%20AI/Day%20Book/.ebextensions/01_fastapi.config) - Elastic Beanstalk configuration.
- [`.env.example`](file:///d:/Shivam%20AI/Shivam%20AI/Day%20Book/.env.example) - Production environment template.
