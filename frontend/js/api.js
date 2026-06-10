const BASE = "";
const USER_ID_KEY = "wp_user_id";

export const userId = () => parseInt(localStorage.getItem(USER_ID_KEY) || "1");
export const setUserId = (id) => localStorage.setItem(USER_ID_KEY, id);

async function req(method, path, body) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(BASE + path, opts);
  if (!res.ok) throw new Error(await res.text());
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Users
  createUser: (u) => req("POST", "/users/", u),
  getUser: (id) => req("GET", `/users/${id}`),
  updateUser: (id, u) => req("PUT", `/users/${id}`, u),
  listUsers: () => req("GET", "/users/"),

  // Exercises
  listExercises: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return req("GET", `/exercises/${qs ? "?" + qs : ""}`);
  },

  // Workouts
  createWorkout: (w) => req("POST", "/workouts/", w),
  listWorkouts: (uid, from, to) => {
    let qs = `user_id=${uid}`;
    if (from) qs += `&from_date=${from}`;
    if (to)   qs += `&to_date=${to}`;
    return req("GET", `/workouts/?${qs}`);
  },
  getWorkout: (id) => req("GET", `/workouts/${id}`),
  deleteWorkout: (id) => req("DELETE", `/workouts/${id}`),
  addSet: (wid, s) => req("POST", `/workouts/${wid}/sets`, s),
  deleteSet: (sid) => req("DELETE", `/workouts/sets/${sid}`),

  // Body weight
  logWeight: (e) => req("POST", "/bodyweight/", e),
  getWeightLog: (uid, from, to) => {
    let qs = `user_id=${uid}`;
    if (from) qs += `&from_date=${from}`;
    if (to)   qs += `&to_date=${to}`;
    return req("GET", `/bodyweight/?${qs}`);
  },

  // Analytics
  muscleVolume: (uid, days = 7) => req("GET", `/analytics/volume?user_id=${uid}&days=${days}`),
  oneRM: (uid, exId) => req("GET", `/analytics/1rm?user_id=${uid}&exercise_id=${exId}`),

  // Calories
  calculateCalories: (data) => req("POST", "/calories/calculate", data),
  weightProjection: (data) => req("POST", "/calories/projection", data),
};
