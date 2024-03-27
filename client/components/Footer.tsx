/* eslint-disable jsx-a11y/anchor-is-valid */
import React from "react"
import { color, fontSize, space, layout, flexbox, typography } from "styled-system"
import logo from "../public/static/logo_tsp.svg"
import Link from "next/link"
import { useTheme } from "@emotion/react"
import styled from "@emotion/styled"

const FooterEl = styled.footer`
  font-family: ${(p) => p.theme.fonts.primary};
  ${space};
  width: 100%;
`
const Container = styled.div`
  background: white;
  box-shadow: 0 -1px 7px 0 rgba(0, 0, 0, 0.05);
`

const Logo = styled.a`
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
  img {
    max-width: 160px;
    margin: auto;
  }
`

const Copyright = styled.div`
  text-align: center;
  letter-spacing: 0.59px;
  text-align: center;
  font-family: ${(p) => p.theme.fonts.secondary};
  ${color}
  ${fontSize}
  ${space}
`

const Ul = styled.ul`
  flex: 1;
  display: flex;
  flex-flow: column wrap;
  ${layout};
  ${space};
  ${typography};
`

const Li = styled.li`
  font-size: ${(p) => p.theme.fontSizes[2]};
  ${space};
`
const Layout = styled.div`
  display: flex;
  justify-content: space-around;
  align-items: center;
  ${space};
  ${flexbox};
  ${space};
  ${typography};
`

export default function Footer({ mt = 5 }) {
  const theme = useTheme()
  return (
    <FooterEl mt={mt}>
      <Container>
        <Layout px={theme.mainPaddingX} pb={4} pt={4} flexDirection={["column", "row"]} textAlign={["center", "left"]}>
          <Logo href="https://theshiftproject.org" target="_blank" rel="noopener noreferrer">
            <img src={logo} alt="Link to The Shift Project Website" />
          </Logo>
          <Ul ml={[0, 5]} height={["auto", "4rem"]}>
            <Li mt={[2, 1]}>
              <Link passHref href="/">
                HOME
              </Link>
            </Li>
            <Li mt={[2, 1]}>
              <Link href="/energy">ENERGY</Link>
            </Li>
            <Li mt={[2, 1]}>
              <Link href="/climate">CLIMATE</Link>
            </Li>
            <Li mt={[2, 1]}>
              <a href="https://theshiftproject.org/nous-contacter/" target="_blank" rel="noopener noreferrer">
                CONTACT
              </a>
            </Li>
            <Li mt={[2, 1]}>
              <Link href="/about">ABOUT</Link>
            </Li>
            <Li mt={[2, 1]}>
              <a href="https://theshiftproject.org" target="_blank" rel="noopener noreferrer">
                THE SHIFT PROJECT
              </a>
            </Li>
            <Li mt={[2, 1]}>
              <Link href="/legal-notice">LEGAL NOTICE</Link>
            </Li>
          </Ul>
        </Layout>
      </Container>
      <Copyright fontSize={3} color="darkBlue" marginTop={2} marginBottom={2}>
        © 2023 The Shift Project. All rights reserved.
      </Copyright>
      <Copyright fontSize={3} color="darkBlue" marginBottom={2}>
        Graciously hosted by <Link href="https://scalingo.com?utm_source=referral&utm_medium=website-footer&utm_campaign=shiftproject">Scalingo</Link> in 🇫🇷
      </Copyright>
    </FooterEl>
  )
}
