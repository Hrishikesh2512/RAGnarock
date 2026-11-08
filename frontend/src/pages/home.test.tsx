import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { HomePage } from "@/pages/home";

describe("HomePage", () => {
  it("renders the application title", () => {
    render(<HomePage />);

    expect(screen.getByRole("heading", { name: "RAGnarock" })).toBeInTheDocument();
  });
});
