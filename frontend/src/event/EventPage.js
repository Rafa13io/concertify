import { useEffect, useState } from "react";
import { Container, div } from "react-bootstrap";
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
    const options = {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    };

    await fetch(`http://localhost:8000/event/${eventId}`, {
      method: "GET",
    })
      .then((response) => {
        if (!response.ok) throw new Error(response.status);
        return response.json();
      })
      .then((data) => {
        setEventData(data);
        setEventData((data) => ({
          ...data,
          start: new Date(data.start).toLocaleDateString(undefined, options),
          end: new Date(data.end).toLocaleDateString(undefined, options),
        }));
      })
      .catch((err) => {
        console.log(err.message);
      });
  };

  useEffect(() => {
    get();
  }, []);

  return (
    <div className="event-details">
      <div className="container-fluid parallax parallax-image"></div>
      <h1 className="event-title text-center">{eventData.title}</h1>
      <div className="event-date text-center">
        {eventData.start} - {eventData.end}
      </div>
      <div className="event-location text-center">
        {eventData.location.address_line}
      </div>
      <div className="event-desc mx-4">
        {eventData.desc}Lorem ipsum dolor sit amet, officia excepteur ex fugiat
        reprehenderit enim labore culpa sint ad nisi Lorem pariatur mollit ex
        esse exercitation amet. Nisi anim cupidatat excepteur officia.
        Reprehenderit nostrud nostrud ipsum Lorem est aliquip amet voluptate
        voluptate dolor minim nulla est proident. Nostrud officia pariatur ut
        officia. Sit irure elit esse ea nulla sunt ex occaecat reprehenderit
        commodo officia dolor Lorem duis laboris cupidatat officia voluptate.
        Culpa proident adipisicing id nulla nisi laboris ex in Lorem sunt duis
        officia eiusmod. Aliqua reprehenderit commodo ex non excepteur duis sunt
        velit enim. Voluptate laboris sint cupidatat ullamco ut ea consectetur
        et est culpa et culpa duis.Lorem ipsum dolor sit amet, officia excepteur
        ex fugiat reprehenderit enim labore culpa sint ad nisi Lorem pariatur
        mollit ex esse exercitation amet. Nisi anim cupidatat excepteur officia.
        Reprehenderit nostrud nostrud ipsum Lorem est aliquip amet voluptate
        voluptate dolor minim nulla est proident. Nostrud officia pariatur ut
        officia. Sit irure elit esse ea nulla sunt ex occaecat reprehenderit
        commodo officia dolor Lorem duis laboris cupidatat officia voluptate.
        Culpa proident adipisicing id nulla nisi laboris ex in Lorem sunt duis
        officia eiusmod. Aliqua reprehenderit commodo ex non excepteur duis sunt
        velit enim. Voluptate laboris sint cupidatat ullamco ut ea consectetur
        et est culpa et culpa duis.Lorem ipsum dolor sit amet, officia excepteur
        ex fugiat reprehenderit enim labore culpa sint ad nisi Lorem pariatur
        mollit ex esse exercitation amet. Nisi anim cupidatat excepteur officia.
        Reprehenderit nostrud nostrud ipsum Lorem est aliquip amet voluptate
        voluptate dolor minim nulla est proident. Nostrud officia pariatur ut
        officia. Sit irure elit esse ea nulla sunt ex occaecat reprehenderit
        commodo officia dolor Lorem duis laboris cupidatat officia voluptate.
        Culpa proident adipisicing id nulla nisi laboris ex in Lorem sunt duis
        officia eiusmod. Aliqua reprehenderit commodo ex non excepteur duis sunt
        velit enim. Voluptate laboris sint cupidatat ullamco ut ea consectetur
        et est culpa et culpa duis.
      </div>
    </div>
  );
};

const PostList = () => {
  return <div>Post List. TBI</div>;
};
