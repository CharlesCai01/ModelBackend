Run the project by gunicorn.  
```bash
gunicorn -w 5 --threads=2  main:app
```