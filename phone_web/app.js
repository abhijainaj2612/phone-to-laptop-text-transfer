const $ = id => document.getElementById(id);
const API_BASE = (window.PC_TYPE_API_BASE || "").replace(/\/$/, "");
const api = path => API_BASE + path;
let auth = JSON.parse(localStorage.getItem("pcTypeAssistant") || "null");

function headers() { return {"Content-Type": "application/json", "Authorization": "Bearer " + auth.token}; }
function show() { $("pair").hidden = !!auth; $("send").hidden = !auth; if (auth) refresh(); }
async function refresh() {
  try {
    const response = await fetch(api("/api/status"), {headers: headers()});
    if (!response.ok) throw new Error();
    const data = await response.json();
    $("connection").textContent = data.pc_online ? "● PC Connected" : "● PC Offline";
    $("connection").className = data.pc_online ? "online" : "offline";
    $("sendButton").disabled = !data.pc_online;
  } catch {
    $("connection").textContent = "● Connection unavailable"; $("connection").className = "offline";
  }
}
$("pairButton").onclick = async () => {
  try {
    const response = await fetch(api("/api/pair"), {method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({code: $("code").value.trim()})});
    const data = await response.json(); if (!response.ok) throw new Error(data.detail);
    auth = data; localStorage.setItem("pcTypeAssistant", JSON.stringify(data)); show();
  } catch (error) { alert(error.message || "Pairing failed"); }
};
$("text").oninput = () => {
  const text = $("text").value;
  $("characters").textContent = `Characters: ${text.length}`;
  $("words").textContent = `Words: ${text.trim() ? text.trim().split(/\s+/).length : 0}`;
};
$("clear").onclick = () => { $("text").value = ""; $("text").dispatchEvent(new Event("input")); };
$("sendButton").onclick = async () => {
  const text = $("text").value;
  if (!text) { $("status").textContent = "Enter some text first."; return; }
  $("sendButton").disabled = true; $("status").textContent = "Sending…";
  try {
    const response = await fetch(api("/api/message"), {method: "POST", headers: headers(), body: JSON.stringify({text})});
    const data = await response.json(); if (!response.ok) throw new Error(data.detail);
    $("status").textContent = "✓ Delivered to PC. Press Ctrl + Shift + T there to type it.";
  } catch (error) { $("status").textContent = "Could not send: " + error.message; }
  finally { refresh(); }
};
$("unpair").onclick = () => { localStorage.removeItem("pcTypeAssistant"); auth = null; show(); };
show(); setInterval(() => auth && refresh(), 15000);
