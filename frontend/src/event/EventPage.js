import { Container } from "react-bootstrap";
import { useCookies } from "react-cookie";
import { useParams } from "react-router-dom";
import EventDetails from "./EventDetails";
import "./EventPage.css";
import JoinButton from "./JoinButton";
import PostList from "./PostList";

export default function EventPage() {
  const { id } = useParams();
  const [cookies, setCookie, removeCookie] = useCookies("[user]");

  return (
    <Container fluid style={{ display: "block", padding: "0" }}>
      <EventDetails eventId={id} />
      {"user" in cookies ? <JoinButton /> : ""}
      <PostList eventId={id} />
    </Container>
  );
}
