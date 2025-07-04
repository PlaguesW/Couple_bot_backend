# Backend

## Running application locally

```shell
pip install -r requirements.txt
```

```shell
python -m uvicorn app.main:app --reload
```

## MVP Structure

<div style="font-family: monospace; background-color: #f5; padding: 15px; border-radius: 5px;">
<pre>
couple_bot_backend/
├── main.py              
├── models.py            
├── schemas.py           
├── database.py          
├── config.py            
├── init_db.py           
├── requirements.txt     
├── Dockerfile          
├── docker-compose.yml  
├── .env.example        
└── README.md                
</pre>
</div>