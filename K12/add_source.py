# app.py - Flask web application
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
import datetime
import json
import sqlite3
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

# Your DataSource and DataSourceManager classes here (same as before)
@dataclass
class DataSource:
    name: str
    date_pulled: datetime.datetime
    source_type: str
    file_path: Optional[str] = None
    record_count: Optional[int] = None
    status: str = 'success'
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[int] = None

class DataSourceManager:
    def __init__(self, db_path: str = "data_sources.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                date_pulled TIMESTAMP NOT NULL,
                source_type TEXT NOT NULL,
                file_path TEXT,
                record_count INTEGER,
                status TEXT DEFAULT 'success',
                notes TEXT,
                metadata TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_source(self, data_source: DataSource) -> DataSource:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(data_source.metadata) if data_source.metadata else None
        
        cursor.execute('''
            INSERT OR REPLACE INTO data_sources 
            (name, date_pulled, source_type, file_path, record_count, status, notes, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data_source.name,
            data_source.date_pulled,
            data_source.source_type,
            data_source.file_path,
            data_source.record_count,
            data_source.status,
            data_source.notes,
            metadata_json
        ))
        
        data_source.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return data_source
    
    def list_sources(self) -> List[DataSource]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM data_sources ORDER BY date_pulled DESC')
        rows = cursor.fetchall()
        conn.close()
        
        sources = []
        for row in rows:
            metadata = None
            if row[8]:
                try:
                    metadata = json.loads(row[8])
                except json.JSONDecodeError:
                    pass
            
            sources.append(DataSource(
                id=row[0],
                name=row[1],
                date_pulled=datetime.datetime.fromisoformat(row[2]) if isinstance(row[2], str) else row[2],
                source_type=row[3],
                file_path=row[4],
                record_count=row[5],
                status=row[6],
                notes=row[7],
                metadata=metadata
            ))
        return sources

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
manager = DataSourceManager()

# HTML Templates as strings (you could also use separate .html files)
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Source Tracker</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem 0; }
        .card { box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: none; }
        .btn-primary { background: #667eea; border-color: #667eea; }
        .form-control:focus { border-color: #667eea; box-shadow: 0 0 0 0.2rem rgba(102,126,234,0.25); }
    </style>
</head>
<body class="bg-light">
    <div class="header text-center">
        <div class="container">
            <h1>📊 Data Source Tracker</h1>
            <p class="lead">Enter and track your data sources</p>
        </div>
    </div>

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="card">
                    <div class="card-header">
                        <h3 class="mb-0">Add New Data Source</h3>
                    </div>
                    <div class="card-body">
                        <form method="POST" action="{{ url_for('add_source') }}">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="name" class="form-label">Data Source Name *</label>
                                        <input type="text" class="form-control" id="name" name="name" required
                                               placeholder="e.g., customer_survey_q3">
                                        <div class="form-text">Enter a unique name for this data source</div>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="source_type" class="form-label">Source Type *</label>
                                        <select class="form-select" id="source_type" name="source_type" required>
                                            <option value="">Choose type...</option>
                                            <option value="csv">CSV File</option>
                                            <option value="excel">Excel File</option>
                                            <option value="api">API</option>
                                            <option value="database">Database</option>
                                            <option value="json">JSON File</option>
                                            <option value="web_scraping">Web Scraping</option>
                                            <option value="manual">Manual Entry</option>
                                            <option value="other">Other</option>
                                        </select>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="file_path" class="form-label">File Path or URL</label>
                                        <input type="text" class="form-control" id="file_path" name="file_path"
                                               placeholder="e.g., /data/customers.csv">
                                    </div>
                                </div>
                                
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="record_count" class="form-label">Number of Records</label>
                                        <input type="number" class="form-control" id="record_count" name="record_count" min="0">
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="status" class="form-label">Status</label>
                                        <select class="form-select" id="status" name="status">
                                            <option value="success">Success</option>
                                            <option value="failed">Failed</option>
                                            <option value="partial">Partial</option>
                                            <option value="in_progress">In Progress</option>
                                        </select>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="collection_date" class="form-label">Collection Date</label>
                                        <input type="date" class="form-control" id="collection_date" name="collection_date"
                                               value="{{ today }}">
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="notes" class="form-label">Notes</label>
                                <textarea class="form-control" id="notes" name="notes" rows="3"
                                          placeholder="Any additional information about this data source..."></textarea>
                            </div>
                            
                            <!-- Additional Fields -->
                            <h5 class="mt-4">Additional Details (Optional)</h5>
                            <div class="row">
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="contact_person" class="form-label">Contact Person</label>
                                        <input type="text" class="form-control" id="contact_person" name="contact_person">
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="data_owner" class="form-label">Data Owner/Dept</label>
                                        <input type="text" class="form-control" id="data_owner" name="data_owner">
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="mb-3">
                                        <label for="file_size" class="form-label">File Size</label>
                                        <input type="text" class="form-control" id="file_size" name="file_size"
                                               placeholder="e.g., 15MB">
                                    </div>
                                </div>
                            </div>
                            
                            <div class="text-center">
                                <button type="submit" class="btn btn-primary btn-lg px-5">
                                    💾 Save Data Source
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <div class="text-center mt-3">
                    <a href="{{ url_for('view_sources') }}" class="btn btn-outline-secondary">
                        📋 View All Sources ({{ source_count }})
                    </a>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

VIEW_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>View Data Sources</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem 0; }
        .source-card { transition: transform 0.2s; }
        .source-card:hover { transform: translateY(-2px); }
    </style>
</head>
<body class="bg-light">
    <div class="header text-center">
        <div class="container">
            <h1>📋 Data Sources</h1>
            <p class="lead">All tracked data sources</p>
        </div>
    </div>

    <div class="container mt-4">
        <div class="row mb-4">
            <div class="col">
                <a href="{{ url_for('index') }}" class="btn btn-primary">➕ Add New Source</a>
                <span class="ms-3 text-muted">{{ sources|length }} total sources</span>
            </div>
        </div>

        {% if sources %}
            <div class="row">
                {% for source in sources %}
                <div class="col-lg-6 mb-4">
                    <div class="card source-card h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">{{ source.name }}</h5>
                            <span class="badge bg-{{ 'success' if source.status == 'success' else 'warning' }}">
                                {{ source.status|title }}
                            </span>
                        </div>
                        <div class="card-body">
                            <p class="card-text">
                                <strong>Type:</strong> {{ source.source_type|title }}<br>
                                <strong>Date:</strong> {{ source.date_pulled.strftime('%Y-%m-%d %H:%M') }}<br>
                                <strong>Records:</strong> {{ source.record_count or 'Unknown' }}<br>
                                {% if source.file_path %}
                                <strong>Path:</strong> {{ source.file_path }}<br>
                                {% endif %}
                            </p>
                            {% if source.notes %}
                            <div class="mt-2">
                                <small class="text-muted"><strong>Notes:</strong> {{ source.notes }}</small>
                            </div>
                            {% endif %}
                            {% if source.metadata %}
                            <div class="mt-2">
                                <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" 
                                        data-bs-target="#metadata-{{ source.id }}">
                                    View Details
                                </button>
                                <div class="collapse mt-2" id="metadata-{{ source.id }}">
                                    <div class="card card-body bg-light">
                                        <pre class="mb-0"><code>{{ source.metadata | tojsonpretty }}</code></pre>
                                    </div>
                                </div>
                            </div>
                            {% endif %}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        {% else %}
            <div class="text-center py-5">
                <h3 class="text-muted">No data sources yet</h3>
                <p>Get started by adding your first data source</p>
                <a href="{{ url_for('index') }}" class="btn btn-primary">Add First Source</a>
            </div>
        {% endif %}
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

@app.route('/')
def index():
    source_count = len(manager.list_sources())
    today = datetime.date.today().isoformat()
    return render_template_string(INDEX_TEMPLATE, source_count=source_count, today=today)

@app.route('/add', methods=['POST'])
def add_source():
    try:
        # Build metadata from form fields
        metadata = {}
        if request.form.get('contact_person'):
            metadata['contact_person'] = request.form['contact_person']
        if request.form.get('data_owner'):
            metadata['data_owner'] = request.form['data_owner']
        if request.form.get('file_size'):
            metadata['file_size'] = request.form['file_size']
        
        # Get collection date or default to today
        collection_date_str = request.form.get('collection_date')
        if collection_date_str:
            collection_date = datetime.datetime.strptime(collection_date_str, '%Y-%m-%d')
        else:
            collection_date = datetime.datetime.now()
        
        # Create data source
        data_source = DataSource(
            name=request.form['name'],
            date_pulled=collection_date,
            source_type=request.form['source_type'],
            file_path=request.form['file_path'] if request.form['file_path'] else None,
            record_count=int(request.form['record_count']) if request.form['record_count'] else None,
            status=request.form['status'],
            notes=request.form['notes'] if request.form['notes'] else None,
            metadata=metadata if metadata else None
        )
        
        manager.add_source(data_source)
        flash(f"✅ Data source '{data_source.name}' added successfully!", 'success')
        
    except Exception as e:
        flash(f"❌ Error adding data source: {str(e)}", 'error')
    
    return redirect(url_for('index'))

@app.route('/sources')
def view_sources():
    sources = manager.list_sources()
    return render_template_string(VIEW_TEMPLATE, sources=sources)

if __name__ == '__main__':
    # For local testing
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    # For production, use:
    # gunicorn -w 4 -b 0.0.0.0:8000 app:app
