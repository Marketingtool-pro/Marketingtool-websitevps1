# How to Run and Set Up n8n for Auto Blog Generator

This guide will help you set up n8n and run the provided auto blog generator workflow on your own system.

## 1. What is n8n?
n8n is a free and open workflow automation tool that lets you connect APIs, automate tasks, and build powerful automations with a visual interface.

## 2. Prerequisites
- Node.js (v16 or later recommended)
- npm (comes with Node.js)
- (Optional) Docker, if you prefer running n8n in a container

## 3. Install n8n
### Option 1: Install via npm
```
npm install n8n -g
```

### Option 2: Run with Docker
```
docker run -it --rm \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

## 4. Start n8n
```
n8n
```
This will start the n8n editor at http://localhost:5678

## 5. Import the Workflow
1. Open the n8n editor in your browser: http://localhost:5678
2. Click the menu (top right) → "Import Workflow".
3. Upload or paste the contents of `auto blog generator.json`.
4. Save the workflow.

## 6. Configure Credentials
- For any HTTP Request or API nodes, set up the required credentials (e.g., Google Gemini API, if used).
- Click on the node with a credential error, then set up or select the correct credential in the right sidebar.

## 7. Set Up Your Django API Endpoint
-open Send Data node and change url path from "http://127.0.0.1:8000/aiwave/api/n8n-create-blog/" to "your-django-server-url/aiwave/api/n8n-create-blog/"
- Make sure your Django server is running and the endpoint `/aiwave/api/n8n-create-blog/` is accessible.
- The workflow will POST new blog data to this endpoint.

## 8. Run the Workflow
- You can run the workflow manually by clicking "Execute Workflow" in n8n.
- Or, enable the schedule trigger to run automatically at the specified time.

## 9. Troubleshooting
- Check the n8n logs for errors.
- Make sure all credentials and endpoints are correct.
- Ensure your Django server is running and accessible from n8n.

## 10. More Resources
- n8n Docs: https://docs.n8n.io/
- n8n Community: https://community.n8n.io/

---

**You are now ready to automate blog post creation using n8n and your Django API!**
