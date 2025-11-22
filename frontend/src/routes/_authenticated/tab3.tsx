import { createFileRoute } from "@tanstack/react-router";
import { Box, Heading, Text } from "@seisveinte/react";

export const Route = createFileRoute("/_authenticated/tab3")({
  component: Tab3Page,
});

function Tab3Page() {
  return (
    <Box p="6">
      <Heading size="8" mb="4">
        Tab 3
      </Heading>
      <Text size="4" color="gray">
        Tab 3 content coming soon...
      </Text>
    </Box>
  );
}
