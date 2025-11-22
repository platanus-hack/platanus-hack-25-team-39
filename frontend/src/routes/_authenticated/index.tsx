import { createFileRoute } from "@tanstack/react-router";
import { Box, Heading, Text, Flex } from "@seisveinte/react";

export const Route = createFileRoute("/_authenticated/")({
  component: HomePage,
});


export function HomePage() {
  return (
    <Box p="6">
      <Flex
        direction="column"
        gap="6"
        align="center"
        style={{ minHeight: "70vh" }}
        justify="center"
      >
        <Box style={{ textAlign: "center", maxWidth: "600px" }}>
          <Heading size="9" mb="4">
            Welcome to Legal Ward
          </Heading>
          <Text size="5" color="gray" mb="4">
            Legal Ward
          </Text>
        </Box>
      </Flex>
    </Box>
  );
}
