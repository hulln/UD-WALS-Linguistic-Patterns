FROM python:3.10-slim
WORKDIR /repo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python", "projects/2_human-vs-ai-svo/scripts/run_stark_svo_analysis.py"]
