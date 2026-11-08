import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StatusBadge } from "@/features/documents/status-badge";

describe("StatusBadge", () => {
  it("renders the document status", () => {
    render(<StatusBadge status="ready" />);

    expect(screen.getByText("ready")).toBeInTheDocument();
  });
});
