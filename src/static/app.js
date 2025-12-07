document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Load activities, render cards with participants, handle signup

  async function fetchActivities() {
    const res = await fetch('/activities');
    if (!res.ok) throw new Error('Failed to fetch activities');
    return await res.json();
  }

  function createAvatar(initials) {
    const span = document.createElement('span');
    span.className = 'avatar';
    span.textContent = initials;
    return span;
  }

  function initialsFromEmail(email) {
    const name = email.split('@')[0] || email;
    const parts = name.split(/[.\-_]/).filter(Boolean);
    if (parts.length === 1) {
      return parts[0].slice(0,2).toUpperCase();
    }
    return (parts[0][0] + (parts[1][0] || '')).toUpperCase();
  }

  function makeParticipantsList(participants) {
    const container = document.createElement('div');
    container.className = 'participants';

    const title = document.createElement('h5');
    title.textContent = 'Participants';
    container.appendChild(title);

    const ul = document.createElement('ul');
    ul.className = 'participants-list';

    if (!participants || participants.length === 0) {
      const li = document.createElement('li');
      const avatar = createAvatar('–');
      const span = document.createElement('span');
      span.className = 'email';
      span.textContent = 'No participants yet';
      li.appendChild(avatar);
      li.appendChild(span);
      ul.appendChild(li);
    } else {
      participants.forEach(email => {
        const li = document.createElement('li');
        const avatar = createAvatar(initialsFromEmail(email));
        const span = document.createElement('span');
        span.className = 'email';
        span.textContent = email;
        li.appendChild(avatar);
        li.appendChild(span);
        ul.appendChild(li);
      });
    }

    container.appendChild(ul);
    return container;
  }

  function renderActivities(activitiesObj) {
    const list = document.getElementById('activities-list');
    const select = document.getElementById('activity');

    // Clear existing
    list.innerHTML = '';
    select.querySelectorAll('option:not([value=""])').forEach(o => o.remove());

    const entries = Object.entries(activitiesObj);
    if (entries.length === 0) {
      list.innerHTML = '<p>No activities available.</p>';
      return;
    }

    entries.forEach(([name, data]) => {
      // Card
      const card = document.createElement('div');
      card.className = 'activity-card';

      const h4 = document.createElement('h4');
      h4.textContent = name;
      card.appendChild(h4);

      const desc = document.createElement('p');
      desc.textContent = data.description;
      card.appendChild(desc);

      const schedule = document.createElement('p');
      schedule.textContent = `Schedule: ${data.schedule}`;
      card.appendChild(schedule);

      const capacity = document.createElement('p');
      capacity.textContent = `Capacity: ${data.participants.length} / ${data.max_participants}`;
      card.appendChild(capacity);

      // Participants section
      const participantsEl = makeParticipantsList(data.participants);
      card.appendChild(participantsEl);

      list.appendChild(card);

      // Option for select
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = name;
      select.appendChild(opt);
    });
  }

  function showMessage(text, type='info') {
    const msg = document.getElementById('message');
    msg.className = '';
    msg.classList.add('message');
    if (type === 'success') msg.classList.add('success');
    else if (type === 'error') msg.classList.add('error');
    else msg.classList.add('info');
    msg.textContent = text;
    msg.classList.remove('hidden');
  }

  async function loadAndRender() {
    try {
      const activities = await fetchActivities();
      renderActivities(activities);
    } catch (err) {
      const list = document.getElementById('activities-list');
      list.innerHTML = '<p>Unable to load activities.</p>';
      showMessage(err.message || 'Error loading activities', 'error');
    }
  }

  // Initialize app
  loadAndRender();

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const activity = document.getElementById("activity").value;

    if (!email || !activity) {
      showMessage('Please provide an email and select an activity.', 'error');
      return;
    }

    try {
      const url = `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`;
      const res = await fetch(url, { method: 'POST' });
      if (!res.ok) {
        const body = await res.json().catch(()=>({detail: 'Unknown error'}));
        throw new Error(body.detail || 'Signup failed');
      }
      const body = await res.json();
      showMessage(body.message || 'Signed up successfully', 'success');
      signupForm.reset();
      await loadAndRender();
    } catch (err) {
      showMessage(err.message || 'Signup failed', 'error');
    }
  });
});
