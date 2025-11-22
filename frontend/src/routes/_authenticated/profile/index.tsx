import { createFileRoute } from "@tanstack/react-router";
import {
  Box,
  Card,
  Flex,
  Heading,
  Text,
  Avatar,
  Badge,
  TextField,
  TextArea,
  Button,
  Separator,
  Grid,
} from "@seisveinte/react";
import { useAuth } from "../../../services/auth";
import { useState } from "react";

export const Route = createFileRoute("/_authenticated/profile/")({
  component: ProfilePage,
});

export function ProfilePage() {
  const { session } = useAuth();
  const [isSaving, setIsSaving] = useState(false);

  const userName = session?.display || session?.email?.split("@")[0] || "User";
  const userInitials = (userName as string).substring(0, 2).toUpperCase();

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Simulate saving
      await new Promise((res) => setTimeout(res, 500));
      // TODO: Implement actual profile update API call
      console.log("Profile saved");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Box p="6">
      <Flex direction="column" gap="6">
        {/* Header */}
        <Flex justify="between" align="center">
          <Heading size="8">User Profile</Heading>
          <Badge color="green" size="3">
            Active
          </Badge>
        </Flex>

        <Separator size="4" />

        {/* Profile Card */}
        <Card>
          <Flex direction="column" gap="5" p="5">
            {/* Avatar Section */}
            <Flex gap="5" align="center">
              <Avatar
                size="7"
                fallback={userInitials}
                radius="full"
                style={{
                  width: "120px",
                  height: "120px",
                }}
              />
              <Flex direction="column" gap="2">
                <Heading size="6">{userName}</Heading>
                <Text size="3" color="gray">
                  {session?.email || "user@email.com"}
                </Text>
                <Flex gap="2">
                  <Badge color="blue">React</Badge>
                  <Badge color="purple">TypeScript</Badge>
                  <Badge color="green">Node.js</Badge>
                  <Badge color="red">PostgreSQL</Badge>
                  <Badge color="yellow">Docker</Badge>
                  <Badge color="pink">Git</Badge>
                  <Badge color="gray">AWS</Badge>
                  <Badge color="cyan">CI/CD</Badge>
                  <Badge color="orange">UI/UX</Badge>
                  <Badge color="brown">Python</Badge>
                </Flex>
              </Flex>
            </Flex>

            <Separator size="4" />

            {/* Contact Information */}
            <Box>
              <Heading size="4" mb="3">
                Contact Information
              </Heading>
              <Grid columns="2" gap="4">
                <Box>
                  <Text size="2" weight="bold" color="gray" mb="1">
                    Email
                  </Text>
                  <TextField.Root
                    defaultValue={session?.email || ""}
                    placeholder="Email"
                    disabled
                  />
                </Box>
                <Box>
                  <Text size="2" weight="bold" color="gray" mb="1">
                    Phone
                  </Text>
                  <TextField.Root
                    defaultValue="+56 9 1234 5678"
                    placeholder="Phone"
                  />
                </Box>
                <Box>
                  <Text size="2" weight="bold" color="gray" mb="1">
                    City
                  </Text>
                  <TextField.Root defaultValue="Santiago" placeholder="City" />
                </Box>
                <Box>
                  <Text size="2" weight="bold" color="gray" mb="1">
                    Country
                  </Text>
                  <TextField.Root defaultValue="Chile" placeholder="Country" />
                </Box>
                <Box>
                  <Text size="2" weight="bold" color="gray" mb="1">
                    Company
                  </Text>
                  <TextField.Root
                    defaultValue="Legal Ward"
                    placeholder="Company"
                  />
                </Box>
                <Box>
                  <Text size="2" weight="bold" color="gray" mb="1">
                    Department
                  </Text>
                  <TextField.Root
                    defaultValue="Development"
                    placeholder="Department"
                  />
                </Box>
              </Grid>
            </Box>

            <Separator size="4" />

            {/* Bio Section */}
            <Box>
              <Heading size="4" mb="3">
                Biography
              </Heading>
              <TextArea
                placeholder="Write something about yourself..."
                defaultValue="Full-Stack Developer who enjoys programming and learning new technologies, always following best practices and company standards."
                style={{ minHeight: "120px" }}
              />
            </Box>

            <Separator size="4" />

            {/* Stats Section */}
            <Box>
              <Heading size="4" mb="3">
                Statistics
              </Heading>
              <Grid columns="4" gap="4">
                <Card>
                  <Flex direction="column" align="center" gap="2" p="3">
                    <Text size="6" weight="bold" color="blue">
                      47
                    </Text>
                    <Text size="2" color="gray">
                      Projects
                    </Text>
                  </Flex>
                </Card>
                <Card>
                  <Flex direction="column" align="center" gap="2" p="3">
                    <Text size="6" weight="bold" color="green">
                      2.5k
                    </Text>
                    <Text size="2" color="gray">
                      Commits
                    </Text>
                  </Flex>
                </Card>
                <Card>
                  <Flex direction="column" align="center" gap="2" p="3">
                    <Text size="6" weight="bold" color="purple">
                      156
                    </Text>
                    <Text size="2" color="gray">
                      Pull Requests
                    </Text>
                  </Flex>
                </Card>
                <Card>
                  <Flex direction="column" align="center" gap="2" p="3">
                    <Text size="6" weight="bold" color="orange">
                      89
                    </Text>
                    <Text size="2" color="gray">
                      Issues
                    </Text>
                  </Flex>
                </Card>
              </Grid>
            </Box>

            {/* Action Buttons */}
            <Flex gap="3" justify="end">
              <Button variant="soft" color="gray" disabled={isSaving}>
                Cancel
              </Button>
              <Button variant="solid" onClick={handleSave} disabled={isSaving}>
                {isSaving ? "Saving..." : "Save Changes"}
              </Button>
            </Flex>
          </Flex>
        </Card>
      </Flex>
    </Box>
  );
}
