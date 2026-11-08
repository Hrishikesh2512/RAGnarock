import { createBrowserRouter } from "react-router";

import { WorkspacePage } from "@/pages/workspace";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <WorkspacePage />,
  },
]);
