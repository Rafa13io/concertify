import { useEffect, useState } from "react";
import { Button, Card, Col, Modal, Row } from "react-bootstrap";
import "./Post.css";

export default function Post({ id, title, desc, votes, image }) {
  const [comments, setComments] = useState([]);
  const [show, setShow] = useState(false);

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  const get = async () => {
    await fetch(`http://localhost:8000/comment?post=${id}`, {
      method: "GET",
    })
      .then((response) => {
        if (!response.ok) throw new Error(response.status);
        return response.json();
      })
      .then((data) => {
        setComments(data.results);
        console.log(data.results);
      })
      .catch((err) => {
        console.log(err.message);
      });
  };

  useEffect(() => {
    get();
  }, []);

  return (
    <>
      <Row
        className="justify-content-center my-3 post"
        key={id}
        onClick={handleShow}
      >
        <Col sm={9} md={8}>
          <Card>
            <Card.Img
              variant="top"
              src="https://media.timeout.com/images/103926031/image.jpg" /* src={image} */
            />
            <Card.Body>
              <Card.Title>{title}</Card.Title>
              <br />
              <Card.Text>{desc}</Card.Text>
              <Button className="float-end">{votes}</Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      <Modal show={show} onHide={handleClose} centered>
        <Modal.Header closeButton>
          <Modal.Title>{title}</Modal.Title>
        </Modal.Header>
        <Modal.Body>{desc}</Modal.Body>
        <Modal.Footer>
          {comments.map((comment) => (
            <p>{comment.desc}</p>
          ))}
        </Modal.Footer>
      </Modal>
    </>
  );
}
