const ENV = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'development' : 'production';
const CONFIG = {
  development: `http://${window.location.hostname}:8001`,
  production: 'https://api.yourdomain.com' // Update this before going live
};
const API = CONFIG[ENV];
let session = null;
let selectedSeat = null;
let selectedMovieId = null;

// Handle Redirects on Page Load
window.onload = () => {
  const path = window.location.pathname;
  const params = new URLSearchParams(window.location.search);
  if (path === '/success') {
    document.getElementById('auth-screen').style.display = 'none';
    document.getElementById('status-screen').style.display = 'flex';
    const mid = params.get('movie_id');
    const row = params.get('row');
    const num = params.get('num');
    fetch(`${API}/payment/confirm/${mid}/${row}/${num}`, {method:'POST'});
  }
};

function showTab(tab) {
  document.getElementById('login-form').classList.toggle('hidden', tab !== 'login');
  document.getElementById('register-form').classList.toggle('hidden', tab !== 'register');
  document.getElementById('tab-login').classList.toggle('active', tab === 'login');
  document.getElementById('tab-register').classList.toggle('active', tab === 'register');
}

async function doLogin() {
  const username = document.getElementById('login-user').value;
  const password = document.getElementById('login-pass').value;
  const res = await fetch(`${API}/login`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username, password}) });
  if (res.ok) { session = await res.json(); startApp(); }
  else { document.getElementById('auth-msg').innerText = "Invalid credentials"; }
}

async function doRegister() {
  const username = document.getElementById('reg-user').value;
  const password = document.getElementById('reg-pass').value;
  const res = await fetch(`${API}/register`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username, password}) });
  if (res.ok) { alert("Registered! Please login."); showTab('login'); }
  else { const data = await res.json(); document.getElementById('auth-msg').innerText = data.detail; }
}

function startApp() {
  document.getElementById('auth-screen').style.display = 'none';
  document.getElementById('app-screen').classList.remove('hidden');
  document.getElementById('nav-username').innerText = session.username.toUpperCase();
  if (session.role === 'admin') {
    document.getElementById('admin-add-section').classList.remove('hidden');
    document.getElementById('admin-table-section').classList.remove('hidden');
  }
  loadMovies();
}

function doLogout() { location.reload(); }

async function loadMovies() {
  const res = await fetch(`${API}/movies`);
  const all = await res.json();
  const movies = session.role === 'admin' ? all : all.filter(m => new Date(m.start_time) > new Date());
  
  document.getElementById('movie-grid').innerHTML = movies.map(m => `
    <div class="movie-card" onclick="selectMovie(${m.movie_id}, '${m.movie_name}')">
      <div class="badge">NOW PLAYING</div>
      <h4 style="margin-top:15px">${m.movie_name}</h4>
      <p style="font-size:13px; color:#94a3b8; margin-top:5px">${m.duration_minutes} mins</p>
    </div>`).join('');
  
  if (session.role === 'admin') {
    document.getElementById('movies-tbody').innerHTML = all.map(m => `
      <tr><td>#${m.movie_id}</td><td>${m.movie_name}</td><td>${new Date(m.start_time).toLocaleString()}</td>
      <td><button class="btn-action danger" style="padding:8px 16px; font-size:12px" onclick="deleteMovie(${m.movie_id})">DELETE</button></td></tr>`).join('');
  }
}

async function selectMovie(id, name) {
  selectedMovieId = id; selectedSeat = null;
  document.getElementById('seat-title').innerText = `SEATING FOR: ${name.toUpperCase()}`;
  document.getElementById('seat-section').style.display = 'block';
  document.getElementById('btn-hold').classList.add('hidden');
  document.getElementById('btn-cancel').classList.add('hidden');
  loadSeats(id);
}

async function loadSeats(movieId) {
  const res = await fetch(`${API}/movies/${movieId}/seats`);
  const seats = await res.json();
  const rows = ['A','B','C','D','E'];
  let html = '';
  rows.forEach(row => {
    html += `<span class="seat-row-label">${row}</span>`;
    for (let n = 1; n <= 10; n++) {
      if (n === 6) html += `<div class="aisle"></div>`;
      const s = seats.find(x => x.row_label.trim() === row && x.seat_number === n);
      const isMine = s && s.username === session.username;
      const status = s.is_booked ? (isMine ? 'booked mine' : 'booked') : 'available';
      const title = s.is_booked ? `By: ${s.username}` : `$${s.price}`;
      html += `<div class="seat ${status}" id="seat-${row}${n}" title="${title}" onclick="chooseSeat('${row}',${n},${isMine})">${n}</div>`;
    }
  });
  document.getElementById('seat-grid').innerHTML = html;
}

function chooseSeat(row, num, isMine) {
  const el = document.getElementById(`seat-${row}${num}`);
  const isBooked = el.classList.contains('booked');
  
  document.querySelectorAll('.seat.selected').forEach(s => s.classList.remove('selected'));
  selectedSeat = {row, num, isMine};

  if (isBooked) {
    document.getElementById('btn-hold').classList.add('hidden');
    document.getElementById('btn-cancel').classList.toggle('hidden', !isMine && session.role !== 'admin');
  } else {
    el.classList.add('selected');
    document.getElementById('btn-hold').classList.remove('hidden');
    document.getElementById('btn-cancel').classList.add('hidden');
  }
}

async function startPayment() {
  const {row, num} = selectedSeat;
  const hold = await fetch(`${API}/reserve/${selectedMovieId}/${row}/${num}`, {
    method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username: session.username})
  });
  if (!hold.ok) return alert("Seat already taken!");
  
  const stripe = await fetch(`${API}/payment/create-session/${selectedMovieId}/${row}/${num}`, {method:'POST'});
  const {checkout_url} = await stripe.json();
  window.location.href = checkout_url;
}

async function cancelBooking() {
  const {row, num} = selectedSeat;
  await fetch(`${API}/reserve/${selectedMovieId}/${row}/${num}`, {
    method:'DELETE', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username: session.username, role: session.role})
  });
  loadSeats(selectedMovieId);
}

async function addMovie() {
  const name = document.getElementById('add-name').value;
  const duration = parseInt(document.getElementById('add-duration').value);
  const start = document.getElementById('add-start').value;
  await fetch(`${API}/movies`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name, duration_minutes: duration, start_time: start}) });
  loadMovies();
}

async function deleteMovie(id) {
  if (confirm("Delete this movie?")) {
    await fetch(`${API}/movies/${id}`, {method:'DELETE'}); loadMovies();
  }
}
