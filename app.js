const form = document.getElementById("userForm");
const userId = document.getElementById("userId");
const fullName = document.getElementById("fullName");
const email = document.getElementById("email");
const phone = document.getElementById("phone");
const role = document.getElementById("role");
const address = document.getElementById("address");
const notes = document.getElementById("notes");
const message = document.getElementById("message");
const formTitle = document.getElementById("formTitle");
const submitBtn = document.getElementById("submitBtn");
const resetBtn = document.getElementById("resetBtn");
const searchInput = document.getElementById("searchInput");
const usersTableBody = document.getElementById("usersTableBody");
const userCount = document.getElementById("userCount");

let users = [];

function showMessage(text, type) {
  message.textContent = text;
  message.className = `message ${type}`;
  setTimeout(() => {
    message.textContent = "";
    message.className = "message";
  }, 3500);
}

function getPayload() {
  return {
    full_name: fullName.value.trim(),
    email: email.value.trim(),
    phone: phone.value.trim(),
    role: role.value.trim(),
    address: address.value.trim(),
    notes: notes.value.trim(),
  };
}

function resetForm() {
  form.reset();
  userId.value = "";
  formTitle.textContent = "Add User";
  submitBtn.textContent = "Save User";
}

function renderUsers(data) {
  userCount.textContent = data.length;

  if (!data.length) {
    usersTableBody.innerHTML = '<tr><td colspan="5" class="empty-state">No users found.</td></tr>';
    return;
  }

  usersTableBody.innerHTML = data
    .map(
      (user) => `
        <tr>
          <td><strong>${escapeHtml(user.full_name)}</strong><br><small>${escapeHtml(user.address || "No address")}</small></td>
          <td>${escapeHtml(user.email)}</td>
          <td>${escapeHtml(user.phone)}</td>
          <td>${escapeHtml(user.role)}</td>
          <td>
            <div class="action-cell">
              <button class="action-btn edit-btn" onclick="editUser(${user.id})">Edit</button>
              <button class="action-btn delete-btn" onclick="deleteUser(${user.id})">Delete</button>
            </div>
          </td>
        </tr>
      `
    )
    .join("");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function loadUsers() {
  const query = searchInput.value.trim();
  const response = await fetch(`/api/users?search=${encodeURIComponent(query)}`);
  users = await response.json();
  renderUsers(users);
}

async function saveUser(event) {
  event.preventDefault();

  const payload = getPayload();
  const isEdit = Boolean(userId.value);
  const url = isEdit ? `/api/users/${userId.value}` : "/api/users";
  const method = isEdit ? "PUT" : "POST";

  const response = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const result = await response.json();

  if (!response.ok) {
    showMessage(result.error || "Something went wrong.", "error");
    return;
  }

  showMessage(isEdit ? "User updated successfully." : "User saved successfully.", "success");
  resetForm();
  await loadUsers();
}

function editUser(id) {
  const selectedUser = users.find((user) => user.id === id);
  if (!selectedUser) return;

  userId.value = selectedUser.id;
  fullName.value = selectedUser.full_name;
  email.value = selectedUser.email;
  phone.value = selectedUser.phone;
  role.value = selectedUser.role;
  address.value = selectedUser.address;
  notes.value = selectedUser.notes;
  formTitle.textContent = "Edit User";
  submitBtn.textContent = "Update User";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function deleteUser(id) {
  const selectedUser = users.find((user) => user.id === id);
  const confirmed = confirm(`Delete ${selectedUser?.full_name || "this user"}?`);
  if (!confirmed) return;

  const response = await fetch(`/api/users/${id}`, { method: "DELETE" });
  const result = await response.json();

  if (!response.ok) {
    showMessage(result.error || "Unable to delete user.", "error");
    return;
  }

  showMessage("User deleted successfully.", "success");
  resetForm();
  await loadUsers();
}

form.addEventListener("submit", saveUser);
resetBtn.addEventListener("click", resetForm);
searchInput.addEventListener("input", loadUsers);

loadUsers();
