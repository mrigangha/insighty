import { push } from "svelte-spa-router";

let isLoggedIn = $state(false);

export function getLoggedIn() {
  return isLoggedIn;
}

export function setLoggedIn(value) {
  isLoggedIn = value;
}

let plan = $state("Free");
export function getPlan() {
  return plan;
}

export function setPlan(value) {
  plan = value;
}

export const URL = "http://localhost:8000";

let open_project_id = $state(-1);

export function getOpenProjectId() {
  return open_project_id;
}

export function setOpenProjectId(id) {
  open_project_id = id;
}

let open_project_name = $state("");

export function setOpenProjectName(name) {
  open_project_name = name;
}

export function getOpenProjectName() {
  return open_project_name;
}

let open_project_trackingkey = $state("");

export function setOpenProjectTrackingKey(key) {
  open_project_trackingkey = key;
}

export function getOpenProjectTrackingKey() {
  return open_project_trackingkey;
}

let open_session_id = $state(-1);

export function setOpenSessionId(id) {
  open_session_id = id;
}

export function getOpenSessionId() {
  return open_session_id;
}

let open_session_lead_id = $state("");

export function setOpenSessionLeadId(id) {
  open_session_lead_id = id;
}

export function getOpenSessionLeadId() {
  return open_session_lead_id;
}

let direct_open_Session = $state(false);

export function setDirectOpenSession(value) {
  direct_open_Session = value;
}

export function getDirectOpenSession() {
  return direct_open_Session;
}

let lead_visitor_id = $state(-1);

export function setLeadVisitorId(id) {
  lead_visitor_id = id;
}

export function getLeadVisitorId() {
  return lead_visitor_id;
}

let access_token = $state("");

export function setAccessToken(token) {
  access_token = token;
}

export function getAccessToken() {
  return access_token;
}

export async function refreshAccessToken() {
  const resp = await fetch(`${URL}/refresh`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (resp.ok) {
    const data = await resp.json();
    setAccessToken(data.access_token);
    return true;
  } else {
    setLoggedIn(false);
    return false;
  }
}

export async function logout() {
  const token = getAccessToken();
  const res = await fetch(`${URL}/logout`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });
  if (res.ok) {
    setLoggedIn(false);
    setAccessToken("");
    push("/");
  }
}

let LoggedInUser = $state({
  name: "",
  email: "",
});

export function setLoggedInUser(name, email) {
  LoggedInUser = { name, email };
}

export function getLoggedInUser() {
  return LoggedInUser;
}
