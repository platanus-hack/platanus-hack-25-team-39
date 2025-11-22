import { createFileRoute } from "@tanstack/react-router";
import { Box, Heading, Text } from "@seisveinte/react";

export const Route = createFileRoute("/_authenticated/tab2")({
  component: Tab2Page,
});

function Tab2Page() {
  return (
    <Box p="6">
      <Heading size="8" mb="4">
        Tab 2
      </Heading>
      <Text size="4" color="gray">
        Tab 2 content coming soon...
      </Text>
    </Box>
  );
}
