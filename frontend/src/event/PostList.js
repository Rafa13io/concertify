import { useEffect, useState } from "react";
import { Button, Card, Col, Nav, Row } from "react-bootstrap";
import { Link } from "react-router-dom";

export default function PostList({ eventId }) {
  const [posts, setPosts] = useState([]);

  const get = async () => {
    await fetch(`http://localhost:8000/post?event=${eventId}`, {
      method: "GET",
    })
      .then((response) => {
        if (!response.ok) throw new Error(response.status);
        return response.json();
      })
      .then((data) => {
        setPosts(data.results);
      })
      .catch((err) => {
        console.log(err.message);
      });
  };

  useEffect(() => {
    get();
  }, []);

  return (
    <div className="post-list m-5">
      {posts.map((post) => (
        <Row className="justify-content-center my-3" key={post.id}>
          <Col sm={9} md={8}>
            <Nav.Link as="div" role="button">
              <Link to="#">
                <Card>
                  <Card.Img
                    variant="top"
                    src="https://media.timeout.com/images/103926031/image.jpg" /* src={post.picture} */
                  />
                  <Card.Body>
                    <Card.Title>{post.title}</Card.Title>
                    <br />
                    <Card.Text>{post.desc}</Card.Text>
                    <Button className="float-end">{post.vote_count}</Button>
                  </Card.Body>
                </Card>
              </Link>
            </Nav.Link>
          </Col>
        </Row>
      ))}
    </div>
  );
}
