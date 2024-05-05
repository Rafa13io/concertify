import { useEffect, useState } from "react";
import { Button, Card, Col, Modal, Row } from "react-bootstrap";
import "./Post.css";
  return (
    <>
      <Row
        className="justify-content-center my-3 post"
        key={id}
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
    </>
  );
}
