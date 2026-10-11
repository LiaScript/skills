module Main exposing (main)

{-| Renders ```ascii blocks the way LiaScript does: same settings, same theme
colors, comment parameters as attributes on the <svg>, caption below.
Verbatim "..." content is shown as plain text (LiaScript parses it as Markdown).
-}

import Browser
import Html exposing (Html)
import Html.Attributes as Attr
import Json.Decode as D
import SvgBob


type alias Block =
    { ascii : String
    , attrs : List ( String, String )
    , caption : Maybe String
    }


type alias Flags =
    { dark : Bool
    , blocks : List Block
    }


decoder : D.Decoder Flags
decoder =
    D.map2 Flags
        (D.field "dark" D.bool)
        (D.field "blocks"
            (D.list
                (D.map3 Block
                    (D.field "ascii" D.string)
                    (D.field "attrs" (D.list (D.map2 Tuple.pair (D.index 0 D.string) (D.index 1 D.string))))
                    (D.field "caption" (D.nullable D.string))
                )
            )
        )


settings : SvgBob.Settings
settings =
    { fontSize = 14.0
    , lineWidth = 1.0
    , textWidth = 8.0
    , textHeight = 16.0
    , arcRadius = 4.0
    , color = { stroke = "#222", text = "black", background = "white" }
    , verbatim = { string = "\"", multiline = True, height = Just "100%", width = Nothing }
    }


viewBlock : Bool -> Block -> Html msg
viewBlock dark block =
    Html.figure [ Attr.class "lia-figure" ]
        [ Html.div [ Attr.class "lia-figure__media" ]
            [ SvgBob.getElements settings block.ascii
                |> SvgBob.setColorsIn
                    (if dark then
                        { text = "white", background = "#323232", stroke = "#ddd" }

                     else
                        { text = "#4b4b4b", background = "white", stroke = "black" }
                    )
                |> SvgBob.drawElements
                    (List.map (\( k, v ) -> Attr.attribute k v) block.attrs)
                    (\str -> Html.div [ Attr.class "verbatim" ] [ Html.text str ])
            ]
        , case block.caption of
            Just c ->
                Html.figcaption [ Attr.class "lia-figure__caption" ] [ Html.text c ]

            Nothing ->
                Html.text ""
        ]


main : Program D.Value (Result D.Error Flags) msg
main =
    Browser.element
        { init = \flags -> ( D.decodeValue decoder flags, Cmd.none )
        , update = \_ m -> ( m, Cmd.none )
        , subscriptions = \_ -> Sub.none
        , view =
            \model ->
                case model of
                    Ok flags ->
                        Html.div [] (List.map (viewBlock flags.dark) flags.blocks)

                    Err e ->
                        Html.pre [] [ Html.text (D.errorToString e) ]
        }
