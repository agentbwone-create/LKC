#!/bin/bash
gunicorn lkc_school.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
```

5. Commit the file

### **Step 2: Update Your Procfile**

Edit your `Procfile` and change it to:
```
web: bash start.sh
