(require [hy.contrib.walk [let]])
(import json
        urllib
        [google.oauth2.service_account [Credentials]]
        [google.auth.transport.requests [AuthorizedSession]]
        [.utils [*]])

(setv SCOPES ["https://www.googleapis.com/auth/cloud-platform"
              "https://www.googleapis.com/auth/userinfo.email"])

(defn make-authed-session-obj [spec]
  (let [creds (.from-service-account-file Credentials
                  (get spec "path-to-key-file"))
        scoped-creds (.with-scopes creds SCOPES)]
    (AuthorizedSession scoped-creds)))

(defn get-pmi-ids [spec session]
  "Returns a set of PMI IDs with date last modified for each."
  (let [url (+ (get spec "base-url") 
                "ParticipantSummary/Modified"
                "?awardee=" (get spec "awardee"))]
    (-> (.get session url)
        (. text)
        (json.loads))))

(defn get-records [spec session &optional [params None] [maxrows None]]
  (let [has-link?
          (fn [bundle]
            (when bundle 
              (and (in "link" bundle) (len (get bundle "link")))))
        get-rcds-from-bundle
          (fn [bundle]
            (lfor x (get bundle "entry") (get x "resource")))
        bld-default-url 
          (fn [] (+ (get spec "base-url")
                    "ParticipantSummary"
                    "?awardee=" (get spec "awardee")
                    (if params
                      (+ "&" (urllib.parse.urlencode params))
                      "")
                    "&count=100"))
        get-page
          (fn [&optional full-url]
            (let [url (if full-url full-url (bld-default-url))]
              (-> (.get session url)
                  (. text)
                  (json.loads))))
        ] ; end of let items
          (setv result-set [])
          (setv bundle (get-page))
          (when bundle (.extend result-set (get-rcds-from-bundle bundle)))
          (while (and (has-link? bundle)
                      (or (not maxrows)
                          (< (len result-set) maxrows)))
            (setv next-link (-> (get bundle "link")
                                (nth 0)
                                (get "url")))
            (setv bundle (get-page next-link))
            (when bundle
              (.extend result-set (get-rcds-from-bundle bundle))))
          result-set))

