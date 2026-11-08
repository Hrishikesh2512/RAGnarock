import { createBrowserRouter } from "react-router-dom";

import { HomePage } from "@/pages/home";
import { RouteErrorPage } from "@/pages/route-error";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <HomePage />,
    errorElement: <RouteErrorPage />,
  },
]);
