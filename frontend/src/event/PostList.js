import { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";

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
    <div className="post-list">
      {posts.map((post) => (
        <Row className="justify-content-center my-3" key={post.id}>
          <Col sm={9} md={8}>
            <Card>
              <Card.Body>
                <Card.Title>{post.title}</Card.Title>
                <br />
                <Card.Text>{post.desc}</Card.Text>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      ))}
    </div>
  );
}
