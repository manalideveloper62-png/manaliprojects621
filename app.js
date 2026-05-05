const API_HOST = window.location.hostname || 'localhost';
const API_BASE = `http://${API_HOST}:8000/api/v1`;
const CHUNK_SIZE = 1024 * 1024 * 5;

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadQueue = document.getElementById('upload-queue');
const fileExplorer = document.getElementById('file-explorer');
const totalStorageEl = document.getElementById('total-storage');
const fileCountEl = document.getElementById('file-count');

// Fetch initial stats and files
async function init() {
    await fetchStats();
    await fetchFiles();
}

async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/files/stats`);
        const data = await res.json();
        totalStorageEl.innerText = formatSize(data.total_size);
        fileCountEl.innerText = data.file_count;
    } catch (e) { console.error('Stats error:', e); }
}

async function fetchFiles() {
    try {
        const res = await fetch(`${API_BASE}/files/`);
        if (!res.ok) throw new Error('Registry offline');
        const files = await res.json();
        fileExplorer.innerHTML = '';
        if (files.length === 0) {
            fileExplorer.innerHTML = '<div style="color: var(--text-dim); grid-column: 1/-1; text-align: center; padding: 40px;">No objects found in infrastructure</div>';
        }
        files.forEach(file => {
            const card = document.createElement('div');
            card.className = 'file-card';
            card.innerHTML = `
                <h4>${file.filename}</h4>
                <p style="font-size: 10px; color: rgba(255,255,255,0.3); margin-bottom: 10px;">${formatSize(file.size)}</p>
                <button class="btn-action" onclick="streamFile(${file.id})">STREAM</button>
                <button class="btn-action" style="background: rgba(239, 68, 68, 0.1); color: #ef4444; margin-top: 5px;" onclick="deleteFile(${file.id})">DELETE</button>
            `;
            fileExplorer.appendChild(card);
        });
    } catch (e) { 
        fileExplorer.innerHTML = `<div style="color: #ef4444; grid-column: 1/-1; text-align: center; padding: 40px; border: 1px dashed #ef444420; border-radius: 20px;">
            Registry Unreachable: ${e.message}<br>
            <span style="font-size: 10px; color: var(--text-dim);">Ensure backend is running on port 8000</span>
        </div>`;
    }
}

async function deleteFile(id) {
    if (!confirm('Delete object?')) return;
    await fetch(`${API_BASE}/files/${id}`, { method: 'DELETE' });
    init();
}

function streamFile(id) {
    const modal = document.getElementById('preview-modal');
    const player = document.getElementById('player');
    player.src = `${API_BASE}/stream/${id}`;
    modal.style.display = 'block';
}

// Modal handling
document.querySelector('.close').onclick = () => {
    document.getElementById('preview-modal').style.display = 'none';
    document.getElementById('player').pause();
}

// Upload Logic
dropZone.onclick = () => fileInput.click();

fileInput.onchange = (e) => {
    const files = e.target.files;
    Array.from(files).forEach(uploadFile);
};

async function uploadFile(file) {
    const id = Math.random().toString(36).substr(2, 9);
    const item = document.createElement('div');
    item.className = 'upload-item';
    item.id = `upload-${id}`;
    item.innerHTML = `
        <div style="font-size: 20px;">📄</div>
        <div class="progress-container">
            <div style="display: flex; justify-content: space-between; font-size: 10px; font-weight: 900; text-transform: uppercase;">
                <span>${file.name}</span>
                <span id="prog-text-${id}">0%</span>
            </div>
            <div class="progress-bar"><div class="progress-fill" id="prog-fill-${id}"></div></div>
            <div id="speed-${id}" style="font-size: 9px; color: var(--primary); margin-top: 5px; font-weight: 700;">WAITING...</div>
        </div>
    `;
    uploadQueue.appendChild(item);

    try {
        const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
        
        // Initiate
        const initFd = new FormData();
        initFd.append('filename', file.name);
        initFd.append('total_chunks', totalChunks);
        initFd.append('file_size', file.size);
        initFd.append('file_type', file.type || 'application/octet-stream');
        
        const initRes = await fetch(`${API_BASE}/uploads/initiate`, { method: 'POST', body: initFd });
        const initData = await initRes.json();
        
        if (!initRes.ok) {
            throw new Error(`Init failed: ${initData.detail || initRes.statusText}`);
        }
        const { upload_id } = initData;

        for (let i = 0; i < totalChunks; i++) {
            const start = i * CHUNK_SIZE;
            const chunk = file.slice(start, start + CHUNK_SIZE);
            const fd = new FormData();
            fd.append('upload_id', upload_id);
            fd.append('chunk_index', i);
            fd.append('chunk', chunk);

            const startTime = Date.now();
            const chunkRes = await fetch(`${API_BASE}/uploads/chunk`, { method: 'POST', body: fd });
            if (!chunkRes.ok) throw new Error(`Chunk ${i} failed`);
            
            const duration = (Date.now() - startTime) / 1000;
            const speed = (chunk.size / (1024 * 1024)) / duration;

            const progress = Math.round(((i + 1) / totalChunks) * 100);
            document.getElementById(`prog-text-${id}`).innerText = `${progress}%`;
            document.getElementById(`prog-fill-${id}`).style.width = `${progress}%`;
            document.getElementById(`speed-${id}`).innerText = `${speed.toFixed(1)} MB/s`;
        }

        const finFd = new FormData();
        finFd.append('upload_id', upload_id);
        finFd.append('filename', file.name);
        finFd.append('total_chunks', totalChunks);
        finFd.append('file_type', file.type || 'application/octet-stream');
        
        const finRes = await fetch(`${API_BASE}/uploads/finalize`, { method: 'POST', body: finFd });
        if (!finRes.ok) throw new Error('Finalize failed');
        
        document.getElementById(`prog-text-${id}`).innerText = 'COMPLETED';
        document.getElementById(`speed-${id}`).innerText = 'UPLOAD SUCCESSFUL';
        init(); 
        setTimeout(() => item.remove(), 5000);
    } catch (e) {
        document.getElementById(`prog-text-${id}`).innerText = 'FAILED';
        let msg = e.message;
        if (typeof e.detail === 'object') msg = JSON.stringify(e.detail);
        document.getElementById(`speed-${id}`).innerText = msg;
        document.getElementById(`speed-${id}`).style.color = '#ef4444';
        console.error(e);
    }
}

function formatSize(b) {
    if (!b) return '0 B';
    const i = Math.floor(Math.log(b) / Math.log(1024));
    return (b / Math.pow(1024, i)).toFixed(1) + ' ' + ['B', 'KB', 'MB', 'GB', 'TB'][i];
}

init();
document.getElementById('refresh-btn').onclick = init;
