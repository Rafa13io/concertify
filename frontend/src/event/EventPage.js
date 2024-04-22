import { useEffect, useState } from "react";
import { Container, Row } from "react-bootstrap";
import { useCookies } from "react-cookie";
import { useParams } from "react-router-dom";
import "./EventPage.css";

export default function EventPage() {
  const { id } = useParams();
  const [cookies, setCookie, removeCookie] = useCookies("[user]");

  return (
    <Container fluid>
      <EventDetails eventId={id} />
      {"user" in cookies ? <SignMeUp /> : ""}
      <PostList />
    </Container>
  );
}

const EventDetails = ({ eventId }) => {
  const initialState = {
    id: -1,
    event_contacts: [],
    social_media: [],
    location: {
      id: -1,
      name: "location",
      address_line: "address",
      postal_code: "00000",
      country: "PL",
    },
    title: "title",
    desc: "description",
    picture: null,
    start: "2024-01-29T04:10:20.904000+01:00",
    end: "2025-03-01T23:33:05.736000+01:00",
  };

  const [eventData, setEventData] = useState(initialState);

  const get = async () => {
    await fetch(`http://localhost:8000/event/${eventId}`, {
      method: "GET",
    })
      .then((response) => {
        if (!response.ok) throw new Error(response.status);
        return response.json();
      })
      .then((data) => {
        setEventData(data);
      })
      .catch((err) => {
        console.log(err.message);
      });
  };

  useEffect(() => {
    get();
  }, []);

  return (
    <Container fluid>
      <Row>
        <h1 className="event-title">{eventData.title}</h1>
      </Row>
      <Row>
        <div className="event-location">{eventData.location.address_line}</div>
      </Row>
      <Row>
        <div className="event-date">
          {eventData.start} - {eventData.end}
        </div>
      </Row>
      <Row>
        <img src="https://weknowyourdreams.com/images/party/party-12.jpg" />
      </Row>
      <Row>
        <div className="event-desc">{eventData.desc}</div>
      </Row>
    </Container>
  );
};

const PostList = () => {
  return <div>Post List. TBI</div>;
};
