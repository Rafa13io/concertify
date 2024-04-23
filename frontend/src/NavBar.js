import { Button, Container, Form, Nav, Navbar } from "react-bootstrap";
import { Link } from "react-router-dom";
import "./NavBar.css";
import { useCookies, Cookies } from "react-cookie";
import { Logout } from "./Login.js";

function UserNavBar() {
  const [cookies] = useCookies([]);
  return (
    <>
      <Nav.Link as="div" role="button">
        <Link to="/new-event">New Event</Link>
      </Nav.Link>
      <Nav.Link as="div" role="button">
        <Link to={"/profile"}>Profile</Link>
      </Nav.Link>
      <Nav.Link as="div" role="button">
        <Logout />
      </Nav.Link>
    </>
  );
}

function GuestNavBar() {
  return (
    <>
      <Nav.Link as="div" role="button">
        <Link to="/login">Login</Link>
      </Nav.Link>
      <Nav.Link as="div" role="button">
        <Link to="/register">Register</Link>
      </Nav.Link>
    </>
  );
}

export default function NavBar() {
  const [cookies, setCookie, removeCookie] = useCookies(["user"]);
  return (
    <Navbar expand="sm" className="sticky-top">
      <Container fluid>
        <Navbar.Brand role="button" id="logo">
          <Link to="/">concertify</Link>
        </Navbar.Brand>
        <Navbar.Toggle />
        <Navbar.Collapse id="navbar-nav" className="justify-content-end">
          <Form className="d-flex">
            <Form.Control type="text" placeholder="Search" className="me-2" />
            <Button type="submit" className="search-button accent-button">
              Search
            </Button>
          </Form>
          <Nav>
            <Nav.Link as="div" role="button">
              <Link to="/cart">Cart</Link>
            </Nav.Link>
            {"user" in cookies ? <UserNavBar /> : <GuestNavBar />}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}
