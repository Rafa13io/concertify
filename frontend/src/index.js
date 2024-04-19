import "bootstrap/dist/css/bootstrap.css";
import { createRoot } from "react-dom/client";
import React from "react";
import App from "./App.js";

const root = createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App/>
  </React.StrictMode>,
);
